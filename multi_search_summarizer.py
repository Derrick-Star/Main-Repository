#!/usr/bin/env python3
"""
multi_search_summarizer.py — Extended Edition (v2)
-------------------------------------------------
Features added (all optional, enabled via CLI flags or top-level config):
- Local SQLite cache + TF-IDF vector store (scikit-learn) for similarity search
- Auto-translate results (googletrans if available)
- On-device summarizer using Hugging Face transformers if installed
- Browser automation renderer (playwright) for JS-heavy pages (optional)
- CLI flags: --dev, --once, --json, --save, --browser, --translate, --local-llm, --mode {speed,heavy}
- Speed/Heavy modes: tune concurrency & max results
- Colored terminal UI using rich if available (fallback to plain text)
- Continuous search loop (unless --once)
- All external integrations are optional; script runs without them (uses safe fallbacks)
- API keys remain optional (set via config or flags)

Usage examples:
  python multi_search_summarizer.py --dev --browser --translate
  python multi_search_summarizer.py --once --mode heavy --local-llm

Notes:
- Install optional dependencies for full capabilities:
    pip install aiohttp beautifulsoup4 duckduckgo-search scikit-learn numpy rich transformers sentence-transformers googletrans==4.0.0-rc1 playwright
- Playwright requires an extra step: `playwright install` (if used).
"""

import argparse
import asyncio
import aiohttp
import sqlite3
import pickle
import time
import json
import os
import sys
from dataclasses import dataclass
from typing import List, Optional

# Optional libs (graceful fallbacks)
try:
    from duckduckgo_search import ddg
except Exception:
    ddg = None

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

try:
    from rich import print as rprint
    from rich.panel import Panel
    from rich.console import Console
    console = Console()
    def out(text, style=None):
        if style:
            console.print(Panel(text, title=style))
        else:
            console.print(text)
except Exception:
    rprint = print
    console = None
    def out(text, style=None):
        print(text)

# Vector / ML libs
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
except Exception:
    TfidfVectorizer = None
    np = None

# Transformers (on-device LLM)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except Exception:
    TRANSFORMERS_AVAILABLE = False

# Sentence transformers (better embeddings)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except Exception:
    SENTENCE_TRANSFORMER_AVAILABLE = False

# Google translate wrapper
try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
except Exception:
    TRANSLATOR_AVAILABLE = False

# Playwright for browser automation
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

# ============================================
# CONFIG — Fill keys here if desired (optional)
# ============================================
SERPAPI_KEY = ""
BING_KEY = ""
BRAVE_KEY = ""
GOOGLE_KEY = ""
GOOGLE_CX = ""

# SQLite cache path
CACHE_DB = os.path.join(os.path.expanduser("~"), ".multisearch_cache_v2.db")

# Default runtime params (can be tuned by CLI mode)
DEFAULTS = {
    "speed": {"max_results": 4, "concurrency": 6, "fetch_timeout": 8},
    "heavy": {"max_results": 12, "concurrency": 12, "fetch_timeout": 16},
}
# ============================================
# MODELS / STRUCTS
# ============================================
@dataclass
class SearchResult:
    provider: str
    title: str
    url: str
    snippet: str
    content: str = ""
    score: float = 0.0

# ============================================
# CACHE / VECTOR STORE (SQLite)
# - stores url -> content, serialized embedding/vector, timestamp
# ============================================
class CacheDB:
    def __init__(self, path=CACHE_DB):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self._init_tables()

    def _init_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            url TEXT PRIMARY KEY,
            title TEXT,
            content BLOB,
            embedding BLOB,
            ts INTEGER
        );
        """)
        self.conn.commit()

    def get(self, url: str):
        cur = self.conn.cursor()
        cur.execute("SELECT title, content, embedding, ts FROM pages WHERE url = ?", (url,))
        r = cur.fetchone()
        if not r:
            return None
        title, raw_content, raw_emb, ts = r
        try:
            content = pickle.loads(raw_content)
        except Exception:
            content = raw_content.decode() if isinstance(raw_content, bytes) else raw_content
        try:
            embedding = pickle.loads(raw_emb) if raw_emb else None
        except Exception:
            embedding = None
        return {"title": title, "content": content, "embedding": embedding, "ts": ts}

    def put(self, url: str, title: str, content: str, embedding=None):
        cur = self.conn.cursor()
        raw_content = pickle.dumps(content)
        raw_emb = pickle.dumps(embedding) if embedding is not None else None
        cur.execute("""
            INSERT OR REPLACE INTO pages (url, title, content, embedding, ts)
            VALUES (?, ?, ?, ?, ?)
        """, (url, title, raw_content, raw_emb, int(time.time())))
        self.conn.commit()

    def close(self):
        self.conn.close()

# ============================================
# UTILITIES
# ============================================
def normalize(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split())

def score_result(res: SearchResult, keywords: List[str]) -> float:
    t = res.title.lower() if res.title else ""
    s = res.snippet.lower() if res.snippet else ""
    c = res.content.lower() if res.content else ""
    sc = 0.0
    for k in keywords:
        if k in t: sc += 3.0
        if k in s: sc += 2.0
        sc += c.count(k) * 0.4
    res.score = sc
    return sc

def extractive_summary(results: List[SearchResult], top_n=5) -> str:
    out_lines = []
    for r in results[:top_n]:
        sn = r.snippet or (r.content[:400] if r.content else "")
        if sn:
            out_lines.append(f"[{r.provider}] {r.title}\n{sn}\n")
    return "\n".join(out_lines) if out_lines else "No extractive summary available."

# ============================================
# OPTIONAL ON-DEVICE SUMMARIZER (transformers)
# Uses seq2seq summarization if available
# ============================================
class LocalSummarizer:
    def __init__(self, model_name: Optional[str] = None):
        self.pipeline = None
        if not TRANSFORMERS_AVAILABLE:
            return
        try:
            model_name = model_name or "facebook/bart-large-cnn"
            self.pipeline = pipeline("summarization", model=model_name)
        except Exception:
            self.pipeline = None

    def summarize(self, text: str, max_length: int = 150) -> str:
        if not self.pipeline or not text:
            return ""
        # chunk long text to avoid OOM
        chunk_size = 1000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        summaries = []
        for ch in chunks:
            try:
                s = self.pipeline(ch, max_length=max_length, min_length=30, truncation=True)
                summaries.append(s[0]["summary_text"])
            except Exception:
                continue
        return " ".join(summaries)

# ============================================
# EMBEDDING / VECTOR FUNCTIONS
# - Prefer sentence-transformers if available
# - Fallback to TF-IDF vectors (sklearn)
# ============================================
class VectorStore:
    def __init__(self):
        self.embeddings = []
        self.urls = []
        self.tfidf = None
        self.sent_model = None
        if SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                self.sent_model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                self.sent_model = None
        if TfidfVectorizer:
            self.tfidf = TfidfVectorizer(max_features=4096)

    def embed_texts(self, texts: List[str]):
        if self.sent_model:
            try:
                embs = self.sent_model.encode(texts, show_progress_bar=False)
                return np.array(embs)
            except Exception:
                pass
        if self.tfidf:
            try:
                X = self.tfidf.fit_transform(texts)
                return X.toarray()
            except Exception:
                pass
        # fallback: simple char-level hashing vector
        out = []
        for t in texts:
            vec = [0]*256
            for ch in t[:2048]:
                vec[ord(ch) % 256] += 1
            out.append(np.array(vec, dtype=float))
        return np.array(out)

    def add(self, url: str, text: str):
        emb = self.embed_texts([text])[0]
        self.embeddings.append(emb)
        self.urls.append(url)

    def similarity_search(self, query: str, k=5):
        if len(self.embeddings) == 0:
            return []
        qv = self.embed_texts([query])[0]
        embs = np.vstack(self.embeddings)
        # cosine similarity
        norms = np.linalg.norm(embs, axis=1) * (np.linalg.norm(qv) + 1e-12)
        sims = (embs @ qv) / norms
        idx = np.argsort(-sims)[:k]
        return [(self.urls[i], float(sims[i])) for i in idx]

# ============================================
# HTML FETCHING: aiohttp + optional Playwright rendering
# ============================================
async def fetch_page_text_aio(session: aiohttp.ClientSession, url: str, timeout:int, debug=False):
    try:
        async with session.get(url, timeout=timeout, headers={"User-Agent":"MultiSearchBot/1.0"}) as resp:
            if resp.status != 200:
                return ""
            ctype = resp.headers.get("Content-Type","")
            text = await resp.text(errors="ignore")
            if "html" in ctype and BeautifulSoup:
                soup = BeautifulSoup(text, "html.parser")
                for tag in soup(["script","style","nav","header","footer","noscript"]):
                    tag.decompose()
                return normalize(soup.get_text(" ", strip=True))[:12000]
            return normalize(text)[:12000]
    except Exception:
        return ""

async def fetch_page_via_playwright(url: str, timeout:int, debug=False):
    if not PLAYWRIGHT_AVAILABLE:
        return ""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=timeout*1000)
            content = await page.content()
            await browser.close()
            if BeautifulSoup:
                soup = BeautifulSoup(content, "html.parser")
                for tag in soup(["script","style","nav","header","footer","noscript"]):
                    tag.decompose()
                return normalize(soup.get_text(" ", strip=True))[:20000]
            return normalize(content)[:20000]
    except Exception:
        return ""

# ============================================
# SEARCH PROVIDERS (async)
# - DuckDuckGo, SerpAPI, Bing, Reddit, Brave, Google, Firefox/Tor via DDG scrape
# - All API calls are optional (skip if key empty)
# ============================================
async def search_ddg(query: str, max_results:int, debug=False):
    if not ddg:
        return []
    try:
        raw = ddg(query, max_results=max_results)
        if debug:
            out(f"[DEBUG] DuckDuckGo raw: {len(raw)} results")
        return [SearchResult("DuckDuckGo", r.get("title",""), r.get("href",""), r.get("body","")) for r in raw]
    except Exception:
        return []

async def search_serpapi(query: str, key: str, max_results:int, debug=False):
    if not key:
        return []
    url = "https://serpapi.com/search.json"
    params = {"q": query, "api_key": key, "num": max_results}
    out_res = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=15) as r:
                data = await r.json()
                if debug:
                    out(f"[DEBUG] SerpAPI returned keys: {list(data.keys())}")
                organic = data.get("organic_results") or data.get("organic") or []
                for item in organic[:max_results]:
                    out_res.append(SearchResult("SerpAPI", item.get("title",""), item.get("link",""), item.get("snippet","")))
    except Exception:
        pass
    return out_res

async def search_bing(query: str, key: str, max_results:int, debug=False):
    if not key:
        return []
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": key}
    out_res = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"q": query, "count": max_results}, headers=headers, timeout=15) as r:
                data = await r.json()
                webv = data.get("webPages", {}).get("value", [])
                for w in webv[:max_results]:
                    out_res.append(SearchResult("Bing", w.get("name",""), w.get("url",""), w.get("snippet","")))
    except Exception:
        pass
    return out_res

async def search_reddit(query: str, max_results:int, debug=False):
    url = "https://api.pushshift.io/reddit/search/submission/"
    params = {"q": query, "size": max_results}
    out_res = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=12) as r:
                data = await r.json()
                for p in data.get("data", [])[:max_results]:
                    snip = (p.get("selftext") or "")[:300]
                    out_res.append(SearchResult("Reddit", p.get("title",""), p.get("full_link",""), snip))
    except Exception:
        pass
    return out_res

async def search_brave(query: str, key: str, max_results:int, debug=False):
    if not key:
        return []
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"X-Subscription-Token": key}
    out_res = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"q": query, "count": max_results}, headers=headers, timeout=12) as r:
                data = await r.json()
                for w in data.get("web", {}).get("results", [])[:max_results]:
                    out_res.append(SearchResult("Brave", w.get("title",""), w.get("url",""), w.get("description","")))
    except Exception:
        pass
    return out_res

async def search_google(query: str, key: str, cx: str, max_results:int, debug=False):
    if not key or not cx:
        return []
    url = "https://www.googleapis.com/customsearch/v1"
    out_res = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"q": query, "key": key, "cx": cx, "num": max_results}, timeout=12) as r:
                data = await r.json()
                for it in data.get("items", [])[:max_results]:
                    out_res.append(SearchResult("Google", it.get("title",""), it.get("link",""), it.get("snippet","")))
    except Exception:
        pass
    return out_res

# DDG HTML scraper for Firefox/Tor mode
async def ddg_html_scrape(query: str, provider_name: str, max_results:int, debug=False):
    url = "https://duckduckgo.com/html/"
    out_res = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data={"q": query}, timeout=12) as r:
                html = await r.text()
                if BeautifulSoup:
                    soup = BeautifulSoup(html, "html.parser")
                    links = soup.select(".result__a")[:max_results]
                    snippets = soup.select(".result__snippet")[:max_results]
                    for a, b in zip(links, snippets):
                        out_res.append(SearchResult(provider_name, a.text.strip(), a.get("href",""), b.text.strip()))
    except Exception:
        pass
    return out_res

# ============================================
# ORCHESTRATION: gather from providers, fetch pages, cache, vectorize, summarize
# ============================================
async def run_search_loop(args):
    # Config by mode
    conf = DEFAULTS.get(args.mode, DEFAULTS["speed"])
    max_results = args.max_results or conf["max_results"]
    concurrency = conf["concurrency"]
    fetch_timeout = conf["fetch_timeout"]

    cache = CacheDB()
    vecstore = VectorStore()
    local_summarizer = LocalSummarizer() if args.local_llm and TRANSFORMERS_AVAILABLE else None
    translator = Translator() if args.translate and TRANSLATOR_AVAILABLE else None

    session = aiohttp.ClientSession()

    try:
        # Continuous loop unless --once
        while True:
            query = args.query if args.query else input("\nSearch > ").strip()
            if not query:
                if args.once:
                    break
                continue
            if query.lower() in ("exit", "quit"):
                out("Exiting.")
                break

            dev_mode = args.dev or ("*dev*" in query.lower())
            if dev_mode:
                out(f"[DEV MODE] Query: {query}", "DEV")

            # Launch provider tasks
            tasks = [
                search_ddg(query, max_results, dev_mode),
                search_serpapi(query, SERPAPI_KEY, max_results, dev_mode),
                search_bing(query, BING_KEY, max_results, dev_mode),
                search_reddit(query, max_results, dev_mode),
                search_brave(query, BRAVE_KEY, max_results, dev_mode),
                search_google(query, GOOGLE_KEY, GOOGLE_CX, max_results, dev_mode),
            ]
            if args.enable_firefox:
                tasks.append(ddg_html_scrape(query, "Firefox", max_results, dev_mode))
            if args.enable_tor:
                tasks.append(ddg_html_scrape(query, "Tor", max_results, dev_mode))

            provider_sets = await asyncio.gather(*tasks, return_exceptions=False)
            all_results = [item for subset in provider_sets for item in subset]

            # Deduplicate by URL/title
            seen = set()
            unique_results = []
            for r in all_results:
                key = (r.url or r.title)[:400]
                if key in seen:
                    continue
                seen.add(key)
                unique_results.append(r)
            all_results = unique_results

            # Limit overall results
            all_results = all_results[: max_results * 6 ]

            # Fetch content (with concurrency and optional playwright)
            sem = asyncio.Semaphore(concurrency)
            async def fetch_content_for(r: SearchResult):
                async with sem:
                    # Check cache
                    cached = cache.get(r.url) if r.url else None
                    if cached:
                        r.content = cached["content"]
                        if dev_mode:
                            out(f"[CACHE HIT] {r.url}")
                        return r
                    # If browser rendering requested, try playwright first
                    content = ""
                    if args.browser and PLAYWRIGHT_AVAILABLE:
                        try:
                            content = await fetch_page_via_playwright(r.url, fetch_timeout, dev_mode)
                            if content:
                                r.content = content
                                cache.put(r.url, r.title, r.content, None)
                                return r
               
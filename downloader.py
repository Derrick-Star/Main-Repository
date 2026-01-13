import os
import re
import requests
from urllib.parse import urlparse, unquote
from pathlib import Path
import mimetypes
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class SmartDownloader:
    def __init__(self, base_path=None):
        if base_path is None:
            self.base_path = Path("/storage/emulated/0/Python Download")
        else:
            self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def detect_source(self, url):
        hostname = urlparse(url).hostname
        if hostname:
            hostname = hostname.replace("www.", "")
            return hostname
        return "Other"

    def convert_to_direct_link(self, url):
        """Convert known platform URLs to direct downloadable links"""
        # GitHub single file
        if 'github.com' in url and '/blob/' in url:
            url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
            return url

        # GitHub repo
        if 'github.com' in url and '/tree/' in url:
            # Download as ZIP of main branch
            parts = urlparse(url).path.split('/')
            if len(parts) >= 3:
                user, repo = parts[1], parts[2]
                return f"https://github.com/{user}/{repo}/archive/refs/heads/main.zip"

        # Google Drive
        if 'drive.google.com' in url:
            match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
            if match:
                file_id = match.group(1)
                return f"https://drive.google.com/uc?export=download&id={file_id}"

        # Dropbox
        if 'dropbox.com' in url:
            url = re.sub(r'\?dl=0$', '?dl=1', url)
            return url

        return url  # leave others unchanged

    def get_filename(self, url, response=None):
        """Extract filename from headers or URL"""
        filename = None
        if response and 'content-disposition' in response.headers:
            cd = response.headers['content-disposition']
            match = re.findall(r'filename\*?=(?:UTF-8\'\')?"?([^\";]+)"?', cd)
            if match:
                filename = unquote(match[0].strip('"'))

        if not filename:
            parsed_url = urlparse(url)
            filename = os.path.basename(unquote(parsed_url.path))

        if not filename or '.' not in filename:
            ext = None
            if response and 'content-type' in response.headers:
                content_type = response.headers['content-type'].split(';')[0]
                ext = mimetypes.guess_extension(content_type)
                if not ext and content_type:
                    ext = '.' + content_type.split('/')[-1]
            filename = f"download{ext or ''}"

        filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
        return filename

    def download(self, url):
        """Download a single URL intelligently"""
        try:
            original_url = url
            url = self.convert_to_direct_link(url)
            print(f"Processing: {original_url}\nConverted to: {url}")

            source = self.detect_source(url)
            folder = self.base_path / source
            folder.mkdir(parents=True, exist_ok=True)

            session = requests.Session()
            retries = Retry(total=3, backoff_factor=1, status_forcelist=[500,502,503,504])
            adapter = HTTPAdapter(max_retries=retries)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            response = session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '').lower()
            filename = self.get_filename(url, response)
            ext = os.path.splitext(filename)[1]

            total_size = int(response.headers.get('content-length', 0))

            # Show file info
            print(f"\nFile Info:\n  Name: {filename}\n  Extension: {ext}\n  Origin: {source}\n  Size: {total_size / (1024*1024):.2f} MB" if total_size > 0 else f"  Size: Unknown")

            # If HTML page (not direct file), ask user
            if 'text/html' in content_type and not any(ext in filename for ext in ['.zip', '.tar', '.gz', '.pdf', '.mp4', '.jpg', '.png', '.txt', '.py']):
                choice = input("✗ This URL is not directly downloadable. Do you want to save it anyway? (y/n): ").strip().lower()
                if choice != 'y':
                    print("Download cancelled.\n")
                    return None

            file_path = folder / filename

            # Handle duplicates
            counter = 1
            orig_file = file_path
            while file_path.exists():
                name, ext = os.path.splitext(orig_file.name)
                file_path = folder / f"{name}_{counter}{ext}"
                counter += 1

            # Download with progress
            downloaded = 0
            chunk_size = 8192
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rProgress: {progress:.1f}%", end='', flush=True)

            print(f"\n✓ Downloaded: {file_path.name}\n  Saved to: {file_path}\n  Origin: {source}\n  Size: {downloaded / (1024*1024):.2f} MB\n")
            return file_path

        except requests.exceptions.RequestException as e:
            print(f"✗ Error: {e}\n")
            return None
        except Exception as e:
            print(f"✗ Unexpected error: {e}\n")
            return None

def main():
    downloader = SmartDownloader()
    while True:
        url = input("Enter a URL (or 'q' to quit): ").strip()
        if url.lower() in ['q', 'quit']:
            break
        if url:
            downloader.download(url)

if __name__ == "__main__":
    main()
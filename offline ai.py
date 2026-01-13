from dotenv import load_dotenv
import os
import openai

# --- Attempt to load .env from SD card ---
env_path = "/storage/723C-11F1/don't touch/my_repo_main/API.env"
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print(f"⚠️ .env not found at {env_path}, fallback to hardcoded key")

# --- Get API key, fallback if needed ---
openai.api_key = os.getenv("OPENAI_API_KEY") or "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"

if not openai.api_key:
    raise ValueError("No API key found. Set it in .env or hardcode it.")

# --- Function to generate code ---
def generate_code(prompt, language="python"):
    language = language.lower()
    system_prompt = f"You are an expert developer. Generate {language} code only."
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()

# --- DevGen CLI ---
if __name__ == "__main__":
    print("🧠 DevGen: Prompt-to-Code CLI")
    print("Type 'exit' to quit.\n")
    while True:
        prompt = input("Prompt> ").strip()
        if prompt.lower() in {"exit", "quit"}:
            break
        lang = input("Language (default python)> ").strip() or "python"
        print("\n" + "="*60 + "\n")
        try:
            result = generate_code(prompt, lang)
            print(result)
        except Exception as e:
            print(f"⚠️ Error generating code: {e}")
        print("\n" + "="*60 + "\n")
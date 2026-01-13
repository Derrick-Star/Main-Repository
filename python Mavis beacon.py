import time
import random
import json
import os

while True:
    SENTENCES = [
        "The quick brown fox jumps over the lazy dog.",
        "Python is a powerful programming language.",
        "Typing speed is measured in words per minute.",
        "Practice makes perfect when learning to type.",
        "OpenAI develops advanced AI technologies."
    ]
    
    SCORE_FILE = "scores.json"
    
    def load_scores():
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r") as f:
                return json.load(f)
        return {}
    
    def save_scores(scores):
        with open(SCORE_FILE, "w") as f:
            json.dump(scores, f, indent=4)
    
    def get_user_scores(scores, username):
        return scores.get(username, [])
    
    def update_user_scores(scores, username, session_data):
        if username not in scores:
            scores[username] = []
        scores[username].append(session_data)
        save_scores(scores)
    
    def typing_test(username):
        target = random.choice(SENTENCES)
        print("\nType the following sentence as fast and accurately as you can:\n")
        print(f'"{target}"\n')
        input("Press Enter when you're ready to start...")
    
        start_time = time.time()
        typed = input("\nStart typing here:\n")
        end_time = time.time()
    
        elapsed = end_time - start_time
        time_minutes = elapsed / 60
        word_count = len(typed.split())
        wpm = word_count / time_minutes
    
        correct_chars = sum(1 for i, c in enumerate(typed) if i < len(target) and c == target[i])
        accuracy = (correct_chars / len(target)) * 100
    
        print("\n--- Results ---")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"WPM: {wpm:.2f}")
        print(f"Accuracy: {accuracy:.2f}%")
    
        return {
            "sentence": target,
            "typed": typed,
            "time_sec": round(elapsed, 2),
            "wpm": round(wpm, 2),
            "accuracy": round(accuracy, 2)
        }
    
    def show_user_summary(scores, username):
        sessions = get_user_scores(scores, username)
        if not sessions:
            print("No previous sessions found.")
            return
        print(f"\n--- {username}'s Typing History ---")
        best_wpm = max(s['wpm'] for s in sessions)
        best_accuracy = max(s['accuracy'] for s in sessions)
        print(f"Sessions: {len(sessions)}")
        print(f"Best WPM: {best_wpm}")
        print(f"Best Accuracy: {best_accuracy}%")
    
    if __name__ == "__main__":
        scores = load_scores()
        user = input("Enter your username: ").strip()
        session = typing_test(user)
        update_user_scores(scores, user, session)
        show_user_summary(scores, user)
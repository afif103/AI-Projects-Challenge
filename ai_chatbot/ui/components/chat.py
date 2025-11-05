# ui/components/chat.py
import requests

BACKEND_URL = "http://localhost:8000/chat"

def send_message(user_input: str, context: str = ""):
    try:
        resp = requests.post(
            BACKEND_URL,
            json={"user_input": user_input, "context": context},
            timeout=180  # ← 3 minutes for first load
        )
        resp.raise_for_status()
        return resp.json()["response"]
    except requests.exceptions.Timeout:
        return "Ollama is loading `llama3.2:3b`... Please wait 30–60 seconds and try again."
    except Exception as e:
        return f"Error: {str(e)}"
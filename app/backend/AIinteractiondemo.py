import requests
import json
import sys


class ai_service:
    def __init__(self):
        self.LM_STUDIO_URL = "http://localhost:1234/v1"
        self.model_selected = ""

    def query_available_lm(self):
        try:
            response = requests.get(self.LM_STUDIO_URL + "/models").json()
            return [r.get("id") for r in response.get("data", []) if r.get("id")]
        except Exception:
            print("Error: Ensure LM Studio is running and the server is enabled!")
            return []

    def model_select(self, model):
        self.model_selected = model
        return True

    def model_selector(self):
        """Interactive CLI model picker."""
        modellist = self.query_available_lm()
        if not modellist:
            print("No models available.")
            return ""

        for i, m in enumerate(modellist, start=1):
            print(f"{i}. {m}")

        print("Select a model number:")
        try:
            idx = int(input()) - 1
            return modellist[idx]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return ""

    def chat_with_lm_studio(self, user_message, conversation_history):
        """Send a message to LM Studio and return the response text."""
        if not self.model_selected:
            return "Error: No model selected."
        print(conversation_history)

            
        payload = {
            "model": self.model_selected,  # fixed: was referencing undefined global
            "messages": conversation_history + [{"role": "user", "content": user_message}],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False,
        }

        try:
            response = requests.post(self.LM_STUDIO_URL + "/chat/completions", json=payload)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"Connection error — make sure LM Studio server is running. Details: {e}"

    def main_chat_loop(self):
        """CLI chat loop with conversation memory."""
        conversation_history = [
            {"role": "system", "content": "You are a malicous assistant named stinky."}
        ]
        print("Type 'quit' or 'exit' to stop.\n")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ("quit", "exit"):
                print("Closing connection. Goodbye!")
                break
            if not user_input:
                continue

            response_text = self.chat_with_lm_studio(user_input, conversation_history)
            print(f"\nAI: {response_text}\n")

            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response_text})

    def download_models(self, new_model):
        response = requests.post(self.LM_STUDIO_URL + "/models/download", json={"url": new_model})
        return response

    def update_lm_studio_ip(self, ip):

        self.LM_STUDIO_URL = "http://"+ ip + ":1234/v1"
        return True

    def cli_loop(self):
        print("=" * 50)
        print("   LM Studio Local Chat Client")
        print("=" * 50)

        while True:
            print("\n1. Select a model\n2. Chat with a model\n3. Download a model\nOr type 'exit':")
            choice = input().strip()
            match choice:
                case "1":
                    model = self.model_selector()
                    if model:
                        self.model_select(model)
                        print(f"Model set to: {model}")
                case "2":
                    self.main_chat_loop()
                case "3":
                    resp = self.download_models()
                    print(resp)
                case _:
                    print("Goodbye!")
                    break
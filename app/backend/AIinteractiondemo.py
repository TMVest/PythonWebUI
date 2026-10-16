import requests
import json
import sys


class ai_service:
    # gemini for the init
    def __init__(self, host="localhost", port="1234", api_token=None):
        self.host = host
        self.port = port
        self.LM_STUDIO_API = f"http://{self.host}:{self.port}/api/v1"
        self.api_token = api_token 
        self.model_loaded = ""
        self.model_selected = ""
        self.response_id = ""

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f" Bearer {self.api_token}"
        return headers

    def query_available_lm(self):
        try:
            response = requests.get(
                f"{self.LM_STUDIO_API}/models",
                
            ).json()
            return [r.get("key") for r in response.get("models") if "key" in r]
        except Exception:
            print("Error: Ensure LM Studio is running and the local server is enabled!")
            return []

    def model_selector(self):
        
        modellist = self.query_available_lm()
        if not modellist:
            print("No models available.")
            return ""

        for i, m in enumerate(modellist, start=1):
            print(f"{i}. {m}")

        print("Select a model number:")
        try:
            idx = int(input().strip()) - 1
            return modellist[idx]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return ""
        
    def load_model(self, selected_model):
        payload = {
            "model": selected_model
        }
        try:
            response = requests.post(
            f"{self.LM_STUDIO_API}/models/load",
            headers = self._get_headers(),
            json = payload
        )
            if response.status_code == 200:
                self.model_selected = selected_model
                self.model_loaded = selected_model
                return response.json()["type"]["instance_id"]["status"]
        except Exception as e:
            return f"Error - failed to load model: {e}"
        return ""


    def unload_model(self):
        payload = {
            "instance_id": self.model_selected
        }
        try:
            response = requests.post(
                f"{self.LM_STUDIO_API}/models/unload",
                headers = self._get_headers(),
                json = payload
            )
            if response.status_code == 200:
                return response.json()["instance_id"]
            
        except Exception as e:
            return f"Error - failed to unload model: {e}"
        return f"Error - model may not have unloaded!"

    def chat_with_lm_studio(self, user_message, response_id = None):
        
        if not self.model_selected:
            return "Error: No model selected."

        payload = {
            "model": self.model_selected,
            "input": user_message,
            "temperature": .69,
            #note to whomever reads this LMSTUDIO docs claim store defaults true. That is a lie.
            "store": True
        }
        if self.response_id:
            payload["previous_response_id"]= self.response_id

   
        response = requests.post(
            f"{self.LM_STUDIO_API}/chat",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        self.response_id = data.get("response_id")
        reply = "".join(item.get("content","") for item in data.get("output",[]) if item.get("type")=="message")
        return reply, data.get("response_id")

    def download_models(self, model_identifier):
        """
        Triggers a model download in LM Studio.
        Accepts model identifiers like 'ibm/granite-4-micro' or direct HuggingFace paths.
        """
        endpoint = f"{self.LM_STUDIO_API}/models/download"
        payload = {"model": model_identifier}

        try:
            response = requests.post(endpoint, headers=self._get_headers(), json=payload)
            return response
        except Exception as e:
            print(f"Failed to reach LM Studio API: {e}")
            return None

    def update_lm_studio_ip(self, ip, port="1234"):
        self.host = ip
        self.port = port
        
        self.LM_STUDIO_API = f"http://{self.host}:{self.port}/api/v1"
        return True

# utils/llm.py
from tests.dev.src.utils.postgresdatabaseconnection import PostgresDatabaseConnection
import os, requests, json
from threading import Lock

_lock = Lock()

class LLMHelper:
    def __init__(self):
        self.db = PostgresDatabaseConnection()
        self.endpoint = os.getenv("OLLAMA_HOST", "http://localhost:11434")  # Added here

    def get_all_models(self):
        result = self.db.read_sql_query("""
            SELECT idllm, txname FROM chatbot_schema.llm ORDER BY idllm;
        """)
        if result is not None and not result.empty:
            return [{"id": row["idllm"], "name": row["txname"]} for _, row in result.iterrows()]
        return []


    def get_model_id_by_name(self, name):
        result = self.db.read_sql_query("""
            SELECT idllm FROM chatbot_schema.llm WHERE txname = %s;
        """, (name,))
        return result[0][0] if result else None

    def get_model_name_by_id(self, idllm):
        result = self.db.read_sql_query("""
            SELECT txname FROM chatbot_schema.llm WHERE idllm = %s;
        """, (idllm,))
        return result[0][0] if result else None    

    def get_default_model_id(self):
        return self.get_model_id_by_name("deepseek-r1")

    def update_chat_model(self, chat_id, llm_id):
        self.db.execute_query("""
            UPDATE chatbot_schema.chat SET idllm = %s WHERE idChat = %s;
        """, (llm_id, chat_id))

    def query_ollama(self, prompt: str, model: str) -> str:
        with _lock:
            try:
                # print(f"[LLM] Querying model '{model}' with prompt: {prompt[:60]}...")
                response = requests.post(
                    f"{self.endpoint}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=60  # ⏱️ Increased timeout
                )
                response.raise_for_status()

                data = response.json()
                # print("[LLM] Response from Ollama:", data)

                return data.get("response", "").strip()

            except requests.exceptions.Timeout:
                print("[LLM] Timeout: The model took too long to respond.")
                return "⚠️ The model took too long to respond. Please try again."

            except Exception as e:
                print(f"[LLM] Error querying Ollama: {e}")
                return "⚠️ Failed to get response from LLM"


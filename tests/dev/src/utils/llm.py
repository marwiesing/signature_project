# utils/llm.py
from tests.dev.src.utils.postgresdatabaseconnection import PostgresDatabaseConnection
import os, requests

class LLMHelper:
    def __init__(self):
        self.db = PostgresDatabaseConnection()

    def get_all_models(self):
        result = self.db.read_sql_query("""
            SELECT idllm, txname FROM chatbot_schema.llm ORDER BY idllm;
        """)
        return [{"id": row[0], "name": row[1]} for row in result] if result else []

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
            UPDATE chatbot_schema.chat SET idllm = %s WHERE idchat = %s;
        """, (llm_id, chat_id))

    def query_ollama(self, prompt: str, model: str) -> str:
        try:
            print(f"[LLM] Querying model '{model}' with prompt: {prompt[:60]}...")
            response = requests.post(self.endpoint, json={
                "model": model,
                "prompt": prompt,
                "stream": False  # Optional: set True to stream chunks
            })
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"[LLM] Error querying Ollama: {e}")
            return "⚠️ Failed to get response from LLM"
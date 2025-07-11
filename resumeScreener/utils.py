import os
from dotenv import load_dotenv

load_dotenv()

def initialize_llm():
   provider = os.getenv("LLM_PROVIDER")
   model_name = os.getenv("LLM_MODEL")
   base_url = os.getenv("LLM_BASE_URL")
   
   if provider == "openai":
       from langchain_openai import ChatOpenAI
       api_key = os.getenv("OPENAI_API_KEY")
       if not api_key:
           raise ValueError("Missing OPENAI_API_KEY")
       llm = ChatOpenAI(model=model_name, api_key=api_key)
       print(f"Using OpenAI model: {model_name}")
   
   elif provider == "ollama":
       from langchain_ollama import OllamaLLM
       if not base_url:
           base_url = "http://localhost:11434"
       llm = OllamaLLM(model=model_name, base_url=base_url)
       print(f"Using Ollama model: {model_name}")
   
   else:
       raise ValueError(f"Unsupported provider: {provider}")
   
   return llm
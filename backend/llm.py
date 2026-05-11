from functools import lru_cache
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    model = os.getenv("OPENAI_MODEL", "openai/gpt-oss-20b:free")
    base_url = os.getenv("OPENAI_BASE_URL")

    if base_url is None and ("/" in model or ":" in model):
        base_url = "https://openrouter.ai/api/v1"

    return ChatOpenAI(
        model=model,
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=base_url,
    )

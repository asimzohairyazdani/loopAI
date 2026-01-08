from langchain_ollama import OllamaLLM
from app.core.config import LLM_MODEL
from app.core.logging import get_logger

logger = get_logger("LLM")


def get_llm():
    """
    Initialize and return OllamaLLM instance.
    """
    try:
        llm = OllamaLLM(model=LLM_MODEL)
        logger.info(f"Initialized OllamaLLM with model: {LLM_MODEL}")
        return llm
    except Exception as e:
        logger.exception(f"Failed to initialize OllamaLLM: {e}")
        raise

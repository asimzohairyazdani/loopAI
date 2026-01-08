

#vectorstore.py
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import (
    FAISS_INDEX_PATH,
    EMBEDDING_MODEL
)
from app.core.logging import get_logger

logger = get_logger("VECTORSTORE")


def build_faiss_index():
    try:
        from app.services.ingestion import load_all_documents
        
        docs = load_all_documents()

        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vectorstore = FAISS.from_texts(docs, embeddings)
        vectorstore.save_local(FAISS_INDEX_PATH)

        logger.info("FAISS index built successfully")

    except Exception:
        logger.exception("Failed building FAISS index")
        raise


def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import FAISS

# from app.core.config import FAISS_DIR, EMBEDDING_MODEL
# from app.core.logging import setup_logger

# logger = setup_logger("VECTORSTORE")


# def build_faiss(docs: list[str]):
#     try:
#         embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
#         store = FAISS.from_texts(docs, embeddings)
#         store.save_local(FAISS_DIR)

#         logger.info("FAISS index built successfully")

#     except Exception:
#         logger.exception("FAISS build failed")
#         raise


# def load_faiss():
#     embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
#     return FAISS.load_local(
#         FAISS_DIR,
#         embeddings,
#         allow_dangerous_deserialization=True
#     )
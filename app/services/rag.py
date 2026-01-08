
import re
import pandas as pd
from app.services.vectorstore import load_vectorstore
from app.core.logging import get_logger
from app.core.config import (
    HOLDINGS_FILE,
    TRADES_FILE,
    FALLBACK_RESPONSE,
    TOP_K,
    SIMILARITY_THRESHOLD,
)
from app.services.llm import get_llm

logger = get_logger("RAG")
vectorstore = load_vectorstore()


# -----------------------------
# STRUCTURED (DETERMINISTIC) QA
# -----------------------------
def try_structured_query(question: str) -> str | None:
    """
    Answer ONLY very specific numeric queries directly from CSVs.
    Returns answer string or None for anything vague/semantic.
    """

    q = question.lower().strip()

    # Only match VERY specific fund count queries with exact fund name
    # Examples: "how many holdings in Fund X?" or "count of trades for Fund Y"
    count_match = re.search(
        r"(count|number|how many|total)\s+(holdings|trades)\s+(in|for)\s+([A-Z][\w\s\-&]*)",
        q,
    )
    if count_match:
        entity = count_match.group(2)
        fund_name = count_match.group(4).strip()

        try:
            holdings_df = pd.read_csv(HOLDINGS_FILE)
            trades_df = pd.read_csv(TRADES_FILE)
        except Exception:
            logger.exception("CSV loading failed")
            return None

        df = holdings_df if entity == "holdings" else trades_df
        fund_cols = [c for c in df.columns if "fund" in c.lower() or "portfolio" in c.lower()]
        if not fund_cols:
            return None

        col = fund_cols[0]
        count = df[df[col].astype(str).str.lower() == fund_name.lower()].shape[0]
        if count > 0:
            logger.info(f"Structured query matched: {entity} count for {fund_name} = {count}")
            return str(count)

    return None  # Let RAG handle everything else


# -----------------------------
# RAG ANSWER
# -----------------------------
def answer_question(question: str) -> str:
    try:
        # 1️⃣ Try structured logic first
        structured_answer = try_structured_query(question)
        if structured_answer:
            logger.info("Answered via structured logic")
            return structured_answer

        # 2️⃣ Retrieval
        results = vectorstore.similarity_search_with_score(question, k=TOP_K)
        logger.info(f"Retrieved {len(results)} docs from vectorstore")

        filtered_docs = [
            doc.page_content
            for doc, score in results
            if score <= SIMILARITY_THRESHOLD
        ]
        logger.info(f"After filtering by threshold ({SIMILARITY_THRESHOLD}): {len(filtered_docs)} docs")

        if not filtered_docs:
            return FALLBACK_RESPONSE

        context = "\n\n".join(filtered_docs)

        llm = get_llm()

        prompt = f"""
You are a chatbot that MUST answer only using the context below.
If the answer is not explicitly present, reply exactly:
"Sorry can not find the answer"

Context:
{context}

Question:
{question}
"""

        response = llm.invoke(prompt).strip()
        logger.info(f"LLM Response (raw): {response[:200] if response else 'EMPTY'}")  # Log first 200 chars

        if (
            not response
            or "sorry" in response.lower()
            or "not found" in response.lower()
            or "cannot find" in response.lower()
        ):
            return FALLBACK_RESPONSE

        return response

    except Exception:
        logger.exception("Error answering question")
        return FALLBACK_RESPONSE
# # app/services/rag.py
# import logging
# from app.core.config import LLM_MODEL, TOP_K
# from app.services.vectorstore import load_faiss

# logger = logging.getLogger("RAG")
# vectorstore = load_faiss()

# # Try LangChain wrapper first (preferred if you use LangChain features)
# try:
#     # langchain-ollama exposes the wrapper for LangChain usage
#     from langchain_ollama.llms import OllamaLLM  # package: langchain-ollama
#     llm = OllamaLLM(model=LLM_MODEL, validate_model_on_init=False)
#     def _llm_invoke(prompt: str) -> str:
#         # OllamaLLM supports invoke(...) which returns an AIMessage or str depending on model type
#         resp = llm.invoke(prompt)
#         # If it's an AIMessage-like object, convert to string:
#         try:
#             return str(resp)
#         except Exception:
#             return resp if isinstance(resp, str) else ""
#     logger.info("Using langchain_ollama.OllamaLLM")
# except Exception:
#     # Fallback: use the official ollama client directly
#     try:
#         from ollama import Client
#         _client = Client()  # points to local ollama server at default http://127.0.0.1:11434
#         def _llm_invoke(prompt: str) -> str:
#             # use generate (or chat) depending on your model; generate returns dict
#             resp = _client.generate(model=LLM_MODEL, prompt=prompt)
#             # example: resp['response'] contains the text
#             return resp.get("response") if isinstance(resp, dict) else str(resp)
#         logger.info("Using ollama.Client fallback")
#     except Exception as e:
#         logger.exception("No available Ollama client; please pip install langchain-ollama or ollama.")
#         # define a safe dummy to avoid crashing imports
#         def _llm_invoke(prompt: str) -> str:
#             return ""

# def answer(question: str) -> str:
#     try:
#         docs = vectorstore.similarity_search(question, k=TOP_K)
#         if not docs:
#             return "Sorry can not find the answer"
#         context = "\n".join(d.page_content for d in docs)

#         prompt = f"""
# Answer ONLY from the data below.
# If answer is not found, say exactly:
# "Sorry can not find the answer"

# DATA:
# {context}

# QUESTION:
# {question}
# """
#         response = _llm_invoke(prompt).strip()
#         return response if response else "Sorry can not find the answer"
#     except Exception:
#         logger.exception("RAG failed")
#         return "Sorry can not find the answer"

##########################################################################################################
# from langchain_ollama import OllamaLLM

# from app.core.config import (
#     FALLBACK_RESPONSE,
#     LLM_MODEL,
#     TOP_K,
#     SIMILARITY_THRESHOLD,
#     MIN_RELEVANT_DOCS
# )
# from app.core.logging import get_logger
# from app.services.vectorstore import load_vectorstore

# logger = get_logger("RAG")

# vectorstore = load_vectorstore()
# llm = OllamaLLM(model=LLM_MODEL)


# def retrieve_docs(question: str) -> list[str]:
#     """
#     Retrieve relevant documents using similarity search with threshold filtering.
#     Industry best practice: Use threshold as soft filter, always return at least top K results.
#     """
#     try:
#         # Get top K candidates
#         results = vectorstore.similarity_search_with_score(question, k=TOP_K)

#         # First try: filter by similarity threshold (FAISS distance - lower is better)
#         relevant_docs = [
#             doc.page_content
#             for doc, score in results
#             if score <= SIMILARITY_THRESHOLD
#         ]

#         # If threshold is too strict, use all top K results (fallback)
#         if not relevant_docs:
#             relevant_docs = [doc.page_content for doc, score in results]
#             logger.warning(
#                 f"No docs passed threshold {SIMILARITY_THRESHOLD}. Using top {len(relevant_docs)} results."
#             )
#         else:
#             logger.info(f"Retrieved {len(relevant_docs)} docs passing threshold {SIMILARITY_THRESHOLD}")
        
#         return relevant_docs

#     except Exception:
#         logger.exception("Retrieval failed")
#         return []


# def answer_question(question: str) -> str:
#     """
#     Answer question using RAG pipeline with industry best practices:
#     1. Retrieve docs with similarity threshold
#     2. Require minimum relevant docs
#     3. Generate answer from context
#     4. Return EXACT fallback if insufficient evidence or LLM cannot answer
#     """
#     try:
#         docs = retrieve_docs(question)

#         # Check if we have enough relevant documents
#         if len(docs) < MIN_RELEVANT_DOCS:
#             logger.warning(
#                 f"Insufficient relevant docs ({len(docs)}/{MIN_RELEVANT_DOCS}) "
#                 f"for question: {question}"
#             )
#             return FALLBACK_RESPONSE

#         context = "\n".join(docs)

#         prompt = f"""STRICT RULES:
# - Answer ONLY if the exact answer exists in the data below
# - If the answer is NOT in the data, respond with EXACTLY: {FALLBACK_RESPONSE}
# - Do NOT explain, infer, assume, or provide partial answers
# - Do NOT say "it seems like", "it might be", "if there was", or similar uncertain phrases
# - Either give a direct factual answer from the data OR respond with: {FALLBACK_RESPONSE}

# DATA:
# {context}

# QUESTION: {question}

# RESPONSE:"""

#         response = llm.invoke(prompt).strip()

#         # If response is empty, return fallback
#         if not response:
#             return FALLBACK_RESPONSE
        
#         # If LLM returned the fallback message, return it
#         if response == FALLBACK_RESPONSE:
#             return FALLBACK_RESPONSE
        
#         # Check if response contains uncertainty, assumptions, or explanations
#         response_lower = response.lower()
#         uncertainty_phrases = [
#             "cannot find", "can not find", "not found", "no information", 
#             "no data", "insufficient", "don't have", "don't know", 
#             "not available", "not mentioned", "not provided", "not in",
#             "it seems", "it might", "if there", "typically", "would be",
#             "could be", "appears to be", "seems like", "not explicitly",
#             "without further", "cannot definitively", "cannot determine",
#             "cannot say", "unclear", "uncertain", "may not"
#         ]
        
#         if any(phrase in response_lower for phrase in uncertainty_phrases):
#             logger.info(f"Response contains uncertainty phrases, returning fallback")
#             return FALLBACK_RESPONSE

#         return response

#     except Exception as e:
#         logger.exception(f"RAG pipeline error: {e}")
#         return FALLBACK_RESPONSE
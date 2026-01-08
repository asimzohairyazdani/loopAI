
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

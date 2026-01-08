#build_index.py

from app.services.ingestion import load_csv_rows
from app.services.vectorstore import build_faiss_index
from app.core.config import HOLDINGS_FILE, TRADES_FILE
from app.core.logging import get_logger

logger = get_logger("BUILD_INDEX")

docs = load_csv_rows(HOLDINGS_FILE) + load_csv_rows(TRADES_FILE)
build_faiss_index()

logger.info("FAISS index build completed successfully")

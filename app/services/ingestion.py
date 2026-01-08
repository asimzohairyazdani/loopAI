
import pandas as pd
from app.core.logging import get_logger
from app.core.config import HOLDINGS_FILE, TRADES_FILE

logger = get_logger("INGESTION")


def load_csv_rows(path: str) -> list[str]:
    """Load individual CSV rows as text documents."""
    try:
        df = pd.read_csv(path)
        logger.info(f"Loaded {len(df)} rows from {path}")

        return [
            " | ".join(f"{k}: {v}" for k, v in row.items())
            for row in df.to_dict(orient="records")
        ]

    except Exception:
        logger.exception(f"Failed reading CSV: {path}")
        raise


def create_comprehensive_summaries() -> list[str]:
    summaries = []

    holdings_df = pd.read_csv(HOLDINGS_FILE)
    trades_df = pd.read_csv(TRADES_FILE)

    # -------- ROW LEVEL DOCS (UNCHANGED IDEA) --------
    for _, row in holdings_df.iterrows():
        summaries.append(" | ".join(f"{k}: {v}" for k, v in row.items()))

    for _, row in trades_df.iterrows():
        summaries.append(" | ".join(f"{k}: {v}" for k, v in row.items()))

    # -------- FUND LEVEL AGGREGATES (FIX) --------
    def fund_level_summary(df, source):
        fund_cols = [c for c in df.columns if "fund" in c.lower() or "portfolio" in c.lower()]
        pl_cols = [c for c in df.columns if "pl_ytd" in c.lower()]

        if not fund_cols:
            return []

        fund_col = fund_cols[0]
        pl_col = pl_cols[0] if pl_cols else None

        output = []
        for fund, g in df.groupby(fund_col):
            text = [f"SOURCE: {source}", f"FUND: {fund}", f"COUNT: {len(g)}"]

            if pl_col:
                g[pl_col] = pd.to_numeric(g[pl_col], errors="coerce")
                text.append(f"PL_YTD_SUM: {g[pl_col].sum():.2f}")
                text.append(f"PL_YTD_MEAN: {g[pl_col].mean():.2f}")

            output.append(" | ".join(text))
        return output

    summaries.extend(fund_level_summary(holdings_df, "HOLDINGS"))
    summaries.extend(fund_level_summary(trades_df, "TRADES"))

    return summaries


def load_all_documents() -> list[str]:
    """Load both individual rows and comprehensive summaries covering all data dimensions."""
    docs = []
    
    # Load individual rows (preserves granular data)
    docs.extend(load_csv_rows(HOLDINGS_FILE))
    docs.extend(load_csv_rows(TRADES_FILE))
    
    # Add comprehensive summaries covering all columns and groupings
    docs.extend(create_comprehensive_summaries())
    
    logger.info(f"Total documents loaded: {len(docs)}")
    return docs

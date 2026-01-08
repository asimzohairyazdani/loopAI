
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
# import pandas as pd
# from app.core.logging import setup_logger

# logger = setup_logger("INGESTION")


# def load_csv_rows(path) -> list[str]:
#     """
#     Load a CSV file and convert each row into a single text string
#     suitable for embedding.
#     """
#     try:
#         df = pd.read_csv(path)
#         logger.info(f"Loaded {len(df)} rows from {path}")

#         rows = []
#         for row in df.to_dict(orient="records"):
#             row_text = " | ".join(f"{k}: {v}" for k, v in row.items())
#             rows.append(row_text)

#         return rows

#     except FileNotFoundError:
#         logger.error(f"File not found: {path}")
#         raise

#     except Exception as e:
#         logger.exception("Failed while loading CSV")
#         raise
######################___________________________________________________________
# #ingestion.py
# import pandas as pd
# from app.core.config import HOLDINGS_FILE, TRADES_FILE
# from app.core.logging import get_logger

# logger = get_logger("INGESTION")


# def load_csv_rows(path: str) -> list[str]:
#     """Load individual CSV rows as text documents."""
#     try:
#         df = pd.read_csv(path)
#         logger.info(f"Loaded {len(df)} rows from {path}")

#         return [
#             " | ".join(f"{k}: {v}" for k, v in row.items())
#             for row in df.to_dict(orient="records")
#         ]

#     except Exception:
#         logger.exception(f"Failed reading CSV: {path}")
#         raise


# def create_comprehensive_summaries() -> list[str]:
#     """Create comprehensive summaries that capture ALL columns and various groupings."""
#     summaries = []
    
#     try:
#         # Load both datasets
#         holdings_df = pd.read_csv(HOLDINGS_FILE)
#         trades_df = pd.read_csv(TRADES_FILE)
        
#         # ===== OVERALL DATASET STATISTICS =====
#         # Holdings overview
#         holdings_summary = [f"HOLDINGS DATA: Total Rows={len(holdings_df)}"]
#         for col in holdings_df.columns:
#             if holdings_df[col].dtype in ['float64', 'int64']:
#                 non_null = holdings_df[col].dropna()
#                 if len(non_null) > 0:
#                     holdings_summary.append(
#                         f"{col}(Total={non_null.sum():.2f}, Mean={non_null.mean():.2f}, "
#                         f"Max={non_null.max():.2f}, Min={non_null.min():.2f})"
#                     )
#             else:
#                 unique_count = holdings_df[col].nunique()
#                 holdings_summary.append(f"{col}(Unique Values={unique_count})")
#         summaries.append(" | ".join(holdings_summary))
#         logger.info("Created overall holdings statistics")
        
#         # Trades overview
#         trades_summary = [f"TRADES DATA: Total Rows={len(trades_df)}"]
#         for col in trades_df.columns:
#             if trades_df[col].dtype in ['float64', 'int64']:
#                 non_null = trades_df[col].dropna()
#                 if len(non_null) > 0:
#                     trades_summary.append(
#                         f"{col}(Total={non_null.sum():.2f}, Mean={non_null.mean():.2f}, "
#                         f"Max={non_null.max():.2f}, Min={non_null.min():.2f})"
#                     )
#             else:
#                 unique_count = trades_df[col].nunique()
#                 trades_summary.append(f"{col}(Unique Values={unique_count})")
#         summaries.append(" | ".join(trades_summary))
#         logger.info("Created overall trades statistics")
        
#         # ===== GROUP SUMMARIES BY ALL AVAILABLE GROUPING COLUMNS =====
#         # For holdings - group by any categorical column
#         for group_col in holdings_df.columns:
#             if holdings_df[group_col].dtype == 'object':
#                 try:
#                     for group_name, group_data in holdings_df.groupby(group_col):
#                         summary_parts = [f"HOLDINGS BY {group_col}={group_name}", f"Count={len(group_data)}"]
                        
#                         # Add all numeric columns with stats
#                         for col in group_data.columns:
#                             if col != group_col and group_data[col].dtype in ['float64', 'int64']:
#                                 non_null = group_data[col].dropna()
#                                 if len(non_null) > 0:
#                                     summary_parts.append(
#                                         f"{col}(T={non_null.sum():.2f}, Avg={non_null.mean():.2f}, "
#                                         f"Max={non_null.max():.2f}, Min={non_null.min():.2f})"
#                                     )
#                             elif col != group_col:
#                                 unique_vals = group_data[col].dropna().unique()
#                                 if len(unique_vals) <= 10:
#                                     summary_parts.append(f"{col}={','.join(str(v)[:10] for v in unique_vals)}")
                        
#                         summaries.append(" | ".join(summary_parts))
#                 except:
#                     pass
        
#         # For trades - group by any categorical column
#         for group_col in trades_df.columns:
#             if trades_df[group_col].dtype == 'object':
#                 try:
#                     for group_name, group_data in trades_df.groupby(group_col):
#                         summary_parts = [f"TRADES BY {group_col}={group_name}", f"Count={len(group_data)}"]
                        
#                         # Add all numeric columns with stats
#                         for col in group_data.columns:
#                             if col != group_col and group_data[col].dtype in ['float64', 'int64']:
#                                 non_null = group_data[col].dropna()
#                                 if len(non_null) > 0:
#                                     summary_parts.append(
#                                         f"{col}(T={non_null.sum():.2f}, Avg={non_null.mean():.2f}, "
#                                         f"Max={non_null.max():.2f}, Min={non_null.min():.2f})"
#                                     )
#                             elif col != group_col:
#                                 unique_vals = group_data[col].dropna().unique()
#                                 if len(unique_vals) <= 10:
#                                     summary_parts.append(f"{col}={','.join(str(v)[:10] for v in unique_vals)}")
                        
#                         summaries.append(" | ".join(summary_parts))
#                 except:
#                     pass
        
#         logger.info(f"Created {len(summaries)} comprehensive summaries")
    
#     except Exception:
#         logger.exception("Failed creating comprehensive summaries")
    
#     return summaries


# def load_all_documents() -> list[str]:
#     """Load both individual rows and comprehensive summaries covering all data dimensions."""
#     docs = []
    
#     # Load individual rows (preserves granular data)
#     docs.extend(load_csv_rows(HOLDINGS_FILE))
#     docs.extend(load_csv_rows(TRADES_FILE))
    
#     # Add comprehensive summaries covering all columns and groupings
#     docs.extend(create_comprehensive_summaries())
    
#     logger.info(f"Total documents loaded: {len(docs)}")
#     return docs
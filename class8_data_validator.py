import logging

logger = logging.getLogger(__name__)

def require_columns(df, required_columns):
    """Check that all required columns exist."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        # logger.error(f"{len(missing_columns)} columns missing")
        logger.error(f"Missing Columns: {",".join(missing_columns)}")
        raise ValueError(f"{len(missing_columns)} columns missing")
    logger.info("All required columns exist")
    return df

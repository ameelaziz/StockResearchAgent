"""Download the latest 10-K for a few tickers and save Item 1A (Risk Factors) as text.

Usage: python ingestion/download_10k.py [TICKER ...]
"""
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from edgar import Company, set_identity

DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA"]
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
SEC_DELAY_SECONDS = 1.0  # SEC allows ~10 req/s; stay well under it


def download_item_1a(ticker: str) -> Path:
    filing = Company(ticker).get_filings(form="10-K").latest()
    tenk = filing.obj()
    text = tenk["Item 1A"]
    if not text:
        raise ValueError(f"{ticker}: Item 1A not found in {filing.accession_no}")

    fiscal_year = str(tenk.period_of_report)[:4]
    out_path = DATA_DIR / ticker / f"{fiscal_year}_10K_item1a.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")

    print(f"{ticker} | filed {filing.filing_date} | period {tenk.period_of_report} "
          f"| accession {filing.accession_no} | {len(text):,} chars -> {out_path}")
    print("   " + text[:300].replace("\n", " ") + "...\n")
    return out_path


def main() -> None:
    load_dotenv()
    set_identity(os.environ["SEC_USER_AGENT"])

    tickers = sys.argv[1:] or DEFAULT_TICKERS
    for i, ticker in enumerate(tickers):
        if i:
            time.sleep(SEC_DELAY_SECONDS)
        download_item_1a(ticker.upper())


if __name__ == "__main__":
    main()

"""Stage 1d: download FRED 30-year mortgage rate (weekly) and CPI-U (monthly). No API key needed."""
from loaders import FRED_FILES
from utils import download, ensure_dirs

if __name__ == "__main__":
    ensure_dirs()
    for series, dest in FRED_FILES.items():
        download(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}", dest)
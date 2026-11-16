"""Stage 1c: download BLS LAUS county annual-average files for 2015-2024."""
from loaders import BLS_FILES
from utils import download, ensure_dirs

if __name__ == "__main__":
    ensure_dirs()
    for year, dest in BLS_FILES.items():
        download(f"https://www.bls.gov/lau/{dest.name}", dest)

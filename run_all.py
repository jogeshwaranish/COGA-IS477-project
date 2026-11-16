# Runs all the scripts in order and checks for errors.
import subprocess
import sys
from pathlib import Path

STAGES = [
    "01_acquire_zillow.py", "02_acquire_acs.py", "03_acquire_bls.py", "04_acquire_fred.py","05_profile_raw.py","06_clean_zillow.py", "07_clean_acs.py", "08_clean_bls.py", "09_clean_fred.py","10_integrate.py",
    "11_quality_post.py",
    # final scripts to come later
]

if __name__ == "__main__":
    scripts = Path(__file__).resolve().parent / "scripts"
    for stage in STAGES:
        subprocess.run([sys.executable, str(scripts / stage)], check=True, cwd=scripts)
    print("Pipeline finished.")

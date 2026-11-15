# COGA Housing Affordability Project

This repository contains the data pipeline and analysis code for the **IS 477** course project investigating U.S. housing affordability across two periods: **2015–2019** and **2020–2024**.

## Quick Start Instructions

### 1. Clone the Repository
Open your terminal, clone the repository, and navigate into the project directory:
```bash
git clone [https://github.com/jogeshwaranish/COGA-IS477-project.git](https://github.com/jogeshwaranish/COGA-IS477-project.git)
cd COGA-IS477-project
```

### 2. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Set Your Census API Key
Set your U.S. Census API key as an environment variable using the command for your operating system:

* **Windows (PowerShell):**
  ```powershell
  $env:CENSUS_API_KEY="your_api_key"
  ```
* **macOS / Linux:**
  ```bash
  export CENSUS_API_KEY="your_key_here"
  ```

### 4. Run the Pipeline
Execute the main script to run the data pipeline and analysis:
```bash
python run_all.py
```
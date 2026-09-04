#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

echo -e "\033[36m[STEP 1] Creating Python virtual environment...\033[0m"
python3 -m venv venv

echo -e "\033[36m[STEP 2] Activating virtual environment...\033[0m"
source venv/bin/activate

echo -e "\033[36m[STEP 3] Installing dependencies...\033[0m"
pip install -r requirements.txt

echo -e "\033[36m[STEP 4] Installing Playwright Chromium browser...\033[0m"
playwright install chromium

echo -e "\033[32m[SUCCESS] Setup complete! Running scraper for 'Photographer' in 'Pune'...\033[0m"
python main.py -c "Photographer" -l "Pune" --headed

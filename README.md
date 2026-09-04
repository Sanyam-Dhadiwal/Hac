# Justdial Scraper (Python Edition)

A lightweight, robust, and production-quality modular Justdial lead scraper built using Python and Playwright. It bypasses common scraping issues (lazy loading, geolocation popups, active overlays) using natural scanning and automated modal dismissals.

---

## Prerequisites

Before setting up the project, make sure you have the following installed on your device:
- **Python** (v3.8 or later)
- **pip** (Python package installer)

---

## Installation & Setup

1. **Open a terminal** inside the project root directory (`pyjd`).
2. **Create a Virtual Environment** (optional but highly recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Install Playwright Browser Binaries** (specifically Chromium):
   ```bash
   playwright install chromium
   ```

---

## How to Run

You can pass the query and options via the CLI. Make sure your virtual environment is activated before running.

### Command Syntax

```bash
python main.py --category "<Category>" --location "<Location>" [--headed]
```

### CLI Arguments

- `-c, --category <string>` *(Required)*: The type of business or service category to scrape (e.g. `"Fashion Designers"`, `"Photographers"`, `"Dentists"`).
- `-l, --location <string>` *(Required)*: The city/location to scope your search (e.g. `"Bengaluru"`, `"Mumbai"`, `"Delhi"`).
- `--headed` *(Optional)*: Runs the scraper with a visible browser window. If omitted, the browser will run invisibly in the background (headless mode).

### Run Examples

**Example 1: Run in the background (Headless mode)**
```bash
python main.py --category "Fashion Designers" --location "Bengaluru"
```

**Example 2: Run with a visible browser window (Headed mode)**
```bash
python main.py --category "Dentists" --location "Mumbai" --headed
```

---

## Scraping Results & Exports

All extracted business records are saved automatically in the `exports/` directory inside the project root:

- **Filename format**: `exports/listings_<YYYY-MM-DD>_<HH-MM-SS>.csv`
- **Fields extracted**:
  - `Name` (Business name)
  - `Rating` (Average customer rating, e.g. `4.8`)
  - `Address` (Full address or block details)
  - `Phone` (Pre-rendered visible phone number, if available)
  - `Verified` (Whether the listing has a "Verified" or "Trusted" badge: `Yes`/`No`)

---

## Core Scraper Features & Evasions

- **Anti-Bot & Automation Stealth**: Uses native evasion scripts to mask the browser's `navigator.webdriver` flag.
- **Bypasses Geolocation Popups**: Pre-grants permissions and mocks coordinates for the targeted search location at the browser context level, natively preventing any location prompt overlays.
- **Smart Modal Overlays Auto-Dismissal**: Spawns a background listener that detects and closes intrusive sign-up or enquiry modals. It implements a `1.5s` delay prior to clicking close buttons to avoid "dead clicks" (clicking before the page script binds event listeners).
- **Viewport Hydration**: Scrolls each business listing card into view before parsing to guarantee that lazy-loaded details (such as names, addresses, and ratings) are fully hydrated and extracted.
- **Zero-Click Phone Retrieval**: Simply reads pre-rendered contact information off the cards without executing any clicks on phone numbers or "Show Number" links for faster execution.

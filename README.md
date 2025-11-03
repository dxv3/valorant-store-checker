# Valorant Store Checker

A Python tool that displays your **Valorant daily store**, **reset timer**, and **VP balance** in a simple generated HTML page.

---

## Features

* Fetches your daily Valorant skin store
* Displays skin names and icons.
* Shows remaining store reset time.
* Displays your current VP balance.
* Automatically opens a clean local HTML page of your store.

---

## Requirements

* Python 3.8 or later
* `requests` module (`pip install requests`)

---

## Setup

1. Clone or download this repository.
2. Install dependencies:

   ```bash
   pip install requests
   ```
3. Open the script and set your **region** in the variable:

   ```python
   REGION = "eu"  # or "na", "ap", "kr"
   ```

---

## Usage

1. Run the script:

   ```bash
   python main.py
   ```
2. A browser window will open asking you to sign in with your Riot account.
3. After login, you will be redirected to a Valorant page. **Copy the full redirected URL**.
4. Paste that URL into the terminal when prompted.
5. The script will:

   * Retrieve your access token
   * Fetch your Valorant store data
   * Generate an `valorant_store.html` file
   * Automatically open it in your browser

---

## Example Output

The HTML file displays:

* Your **VP balance**
* Store reset countdown
* The four current daily offers with **names** and **images**

---

## Notes

* The script only works for accounts that have logged in to Valorant at least once.
* Riot’s API is unofficial for store access; this may break if endpoints change.
* Use your **own account only**. Do not share tokens or data.

---

## License

This project is for **educational and personal use only**. Not affiliated with Riot Games.

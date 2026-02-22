# Telegram Leaks Scraper

This script collects cybersecurity-related leaks from **Telegram channels** that are relevant to Tunisia. It uses a combination of **keyword filtering**, **translation**, and **LLM-based text generation** to extract structured information.

---

## Features

* Connects to public or private Telegram channels using **Telethon**.
* Fetches recent messages from channels, avoiding duplicates via a `last_seen_messages` table.
* Detects messages containing:

  * **Tunisian keywords**: `"Tunisia"`, `"Tunis"`, `".tn"`, `"+216"`, etc.
  * **Cybersecurity-related keywords**: `"hack"`, `"breach"`, `"leak"`, `"malware"`, etc.
* Translates messages to English if necessary for consistent LLM processing.
* Generates:

  * **Leak title** (short, professional, factual)
  * **Leak description** (one-sentence summary)
* Extracts metadata:

  * Message ID, author, channel URL, post date
  * Attached images (first photo only, stored as bytes)
  * Tunisian domains mentioned (`.tn`)
* Saves extracted information in **SQLite** database (`leaks.db`) under the table `telegram_leaks`.

---

## Requirements

* Python 3.13+
* Telethon (`pip install telethon`)
* GPT4All (`pip install gpt4all`)
* googletrans (`pip install googletrans`)
* SQLite3 (bundled with Python)
* Telegram **API ID** and **API Hash** (via `.env` file)
* Logged-in Telegram session or access to public channels.

---

## Setup

1. Create a `.env` file in your project root with your Telegram API credentials:

```env
API_ID=your_api_id
API_HASH=your_api_hash
```

2. Ensure `sqlite_connection` package is available to save messages in `leaks.db`.

---

## Usage

```bash
python -m Telegram.search_and_scrape_from_telegram
```

> The script will iterate over the channels listed in `channels`, translate messages if needed, generate leak titles/descriptions, and store all information in the database.

---

## Database

* **Database file:** `leaks.db`

* **Table:** `telegram_leaks`

* **Columns:**

  * `id` (TEXT, primary key) – combination of channel URL and message ID
  * `channel_url` (TEXT)
  * `message_id` (INTEGER)
  * `leak_name` (TEXT)
  * `leak_description` (TEXT)
  * `raw_text` (TEXT)
  * `leak_date` (DATETIME)
  * `leak_link` (TEXT)
  * `leak_image` (BLOB)

* **Associated domains:** Stored in `telegram_leak_domains` table.

---

## Notes

* **Message translation** is performed to ensure consistent English input for the LLM.
* Only messages containing both **Tunisian keywords** and **cyberattack keywords** are processed.
* Images are saved as bytes in the database; only the **first image** in a message is considered.
* Domains ending with `.tn` are extracted automatically and associated with the post.
* For best results, maintain your **Telegram session** active or use public channels only.
* The LLM is used for **title and description generation**, producing professional summaries suitable for threat monitoring.


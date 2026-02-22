# Forums Scraper

These scripts collect data leaks from **Darkforums.me** and **Patched.to** using the keyword `"tunisia"`.

---

## Features

* Automates browser interactions with **Playwright**.
* Extracts thread data including:

  * Thread title
  * Author
  * Forum name
  * Number of replies and views
  * Post date
  * Link to the thread
  * Screenshot of the post
* Saves all data into an SQLite database (`leaks.db`) under the table `forums_leaks`.
* Uses **Opera GX** with your existing profile to stay logged in.

---

## Requirements

* Python 3.13+
* Playwright (`pip install playwright`)
* SQLite3 (bundled with Python)
* Logged-in accounts on **Darkforums.me** and **Patched.to**
* DOM structure of websites must be maintained; update selectors if websites change.

---

## Usage

Run the scripts from the project root directory (`Code/`):

```bash
# Darkforums
python -m Forums.darkforums.search_and_scrape_from_darkforums

# Patched.to
python -m Forums.patched.search_and_scrape_from_patched
```

> **Note:** Ensure Opera GX is closed before running, and you are logged in with your profile.

---

## Database

* **Database file:** `leaks.db`
* **Table:** `forums_leaks`
* **Columns:**

  * `id` (INTEGER, primary key)
  * `name` (TEXT) – Thread title
  * `forums_website` (TEXT)
  * `author` (TEXT)
  * `forum` (TEXT)
  * `link` (TEXT, unique)
  * `post_date` (TEXT)
  * `screenshot_path` (TEXT)

---

## Notes

* Scripts are dependent on the website’s DOM structure; changes in the forum layout may require updating selectors.
* Always keep your browser profile logged in for successful scraping.
* Screenshots are stored in `Forums/threads_screenshots/`.

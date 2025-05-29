# Instagram Reels Scraper (Pyppeteer Version) ![Python](https://img.shields.io/badge/python-3.8%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

> **Automate Instagram Reels metadata collection from public accounts using Python and Pyppeteer.**

---

## 🚀 Features

- **Detailed Reel Data:** Extracts shortcode, URL, caption, and publication date for each reel.
- **Multi-Account Scraping:** Scrape reels from a list of target usernames in one run.
- **Session Persistence:** Saves/loads login cookies to minimize manual logins.
- **Secure Credentials:** Loads Instagram username/password from a `.env` file (never commit this file!).
- **Proxy Support:** Optional proxy rotation for safer, distributed scraping.
- **Modular Codebase:** Clean, maintainable Python package structure.
- **Structured Output:** Saves results in a well-formatted JSON file.

---

## 🖼️ Example Screenshot

Below is an example of the scraper running in non-headless mode, automating the login and scraping process:

![Scraper in Action](screenshots/example_scraper.png)

---

## 🗂️ Project Structure

```
igscrapper/
├── igscraper/           # Core package (browser, login, scraping logic)
├── main.py              # Main script entry point
├── accounts.txt         # (Optional) List of target usernames, one per line
├── .env.example         # Example environment file
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── reels_results.json   # Output (created after run)
├── instagram_cookies.json # Saved cookies (created after login)
└── screenshots/         # Error/debug screenshots
```

---

## ⚡ Quick Start

1. **Clone the repository:**
    ```bash
    git clone https://github.com/mazithesage/igscrapper.git
    cd igscrapper
    ```
2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Set up your `.env` file:**
    - Copy `.env.example` to `.env` and fill in your Instagram credentials:
      ```env
      INSTAGRAM_USERNAME="your_instagram_username"
      INSTAGRAM_PASSWORD="your_instagram_password"
      # Optional: PROXY_LIST_FILE=./proxies.txt
      ```
    - **Never commit your `.env` file!** It is already in `.gitignore`.
4. **Add target accounts:**
    - Edit `accounts.txt` and list one Instagram username per line (no @ symbol).
5. **Run the scraper:**
    ```bash
    python3 main.py
    ```

---

## 🎯 Target Account Setup

- By default, the scraper reads target usernames from `accounts.txt` (one per line).
- Alternatively, you can edit the `target_usernames` list in `main.py`.

---

## 📝 Output

- Results are saved to `reels_results.json` as a dictionary:
  ```json
  {
    "nasa": [
      { "shortcode": "C8...", "url": "https://www.instagram.com/nasa/reel/C8.../", ... },
      ...
    ],
    "natgeo": [ ... ]
  }
  ```
- Screenshots of errors (if any) are saved in the `screenshots/` directory.

---

## ⚙️ Advanced Usage

### Run in Headless Mode
By default, the browser may open visibly for debugging. To run in headless mode, edit the `setup_browser` function in `igscraper/browser.py` and set `headless=True`:
```python
browser = await launch(headless=True, ...)
```

### Custom Delays & Timeouts
You can adjust scraping speed and timeouts in `igscraper/config.py`:
- `SHORT_DELAY_MS` — General short delay (ms)
- `EXPLICIT_WAIT_TIMEOUT_S` — Max wait for selectors (s)

### Command-Line Arguments (If Implemented)
If you add CLI support, you could run:
```bash
python3 main.py --accounts my_accounts.txt --output my_results.json
```
*(Modify the script to support these options if needed!)*

---

## 🛠️ Updating Selectors
Instagram frequently changes its HTML structure. If scraping fails or returns empty data:
- Open the target Instagram page in your browser.
- Use Developer Tools (F12) to inspect the elements for reels, captions, etc.
- Update the selectors in `igscraper/scraper.py` accordingly.

---

## 🐳 Docker Support (Optional)
Want to run the scraper in a containerized environment? Add a `Dockerfile` like this:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]
```
Then build and run:
```bash
docker build -t igscrapper .
docker run --env-file .env -v $(pwd)/accounts.txt:/app/accounts.txt igscrapper
```

---

## 🔒 Security & Best Practices

- **Never share or commit your `.env` file.**
- Use a dedicated Instagram account for scraping, not your personal one.
- Respect Instagram's [Terms of Service](https://www.instagram.com/about/legal/terms/).
- Use proxies if scraping at scale to avoid rate limits and blocks.

---

## 🛠️ Troubleshooting

- **Login failed:**
  - Double-check credentials in `.env`.
  - Delete `instagram_cookies.json` to force a fresh login.
  - Watch the browser window for unexpected prompts.
- **No data in `reels_results.json`:**
  - Check for errors in the console.
  - Target accounts may be private or have no reels.
  - Selectors may need updating if Instagram changed their site.
- **Script crashes:**
  - Ensure all dependencies are installed.
  - Note the full error message and traceback.

---

## 💡 FAQ

**Q: Can I use this for private accounts?**  
A: No, only public accounts are supported.

**Q: How do I enable proxy rotation?**  
A: Add a file with proxies (one per line) and set `PROXY_LIST_FILE=./proxies.txt` in your `.env`.

**Q: Does this handle 2FA?**  
A: Yes, if prompted, you will be asked to enter the 2FA code in the terminal.

**Q: Can I run this on a server or cloud VM?**  
A: Yes! Use headless mode and ensure all dependencies (including Chromium) are available. Docker is recommended for reproducibility.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 🙋‍♂️ Support & Contact

- For bugs, open an [issue](https://github.com/mazithesage/igscrapper/issues).
- For questions, suggestions, or help, start a [discussion](https://github.com/mazithesage/igscrapper/discussions) or email the maintainer at `your.email@example.com`.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🚀 Performance Tips & Optimization

- **Adjust Delays:** Modify `SHORT_DELAY_MS` in `igscraper/config.py` to balance speed and reliability. Lower values speed up scraping but increase the risk of rate limiting.
- **Use Proxies:** Rotate proxies to distribute requests and avoid IP bans. Set `PROXY_LIST_FILE` in your `.env` file.
- **Headless Mode:** Run in headless mode (`headless=True`) for faster execution and lower resource usage.
- **Batch Processing:** Scrape fewer accounts per run to reduce the risk of being blocked. Use a scheduler (e.g., cron) to automate multiple runs.

---

## 🛠️ Error Handling & Logging

- **Enable Detailed Logging:** Set `LOG_LEVEL=DEBUG` in your `.env` file for verbose logs. Check `scraper.log` for detailed error messages.
- **Common Errors:**
  - **Login Failed:** Verify credentials and check for 2FA prompts.
  - **Selector Errors:** Update selectors in `igscraper/scraper.py` if Instagram changes its layout.
  - **Network Issues:** Ensure stable internet and proxy settings.
- **Screenshots:** Error screenshots are saved in the `screenshots/` directory for debugging.

---

## 🔄 Integration Examples

- **Data Analysis:** Use the scraped data in `reels_results.json` for analysis with tools like Pandas or Jupyter Notebooks.
- **Automation:** Integrate with CI/CD pipelines or schedulers (e.g., cron, GitHub Actions) for automated scraping.
- **APIs:** Extend the scraper to feed data into APIs or databases (e.g., MongoDB, PostgreSQL) for real-time analytics.

---

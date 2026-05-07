#!/usr/bin/env python3
"""
Run this script from your thrift-investment project folder.
It downloads the fonts from Google, saves them locally,
generates a fonts.css, and updates all HTML files.

Usage:
  cd thrift-investment
  python3 setup-fonts.py
"""

import os
import re
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

GOOGLE_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Playfair+Display:wght@400;700;900"
    "&family=DM+Sans:wght@300;400;500"
    "&display=swap"
)

HTML_FILES = [
    "index.html",
    "deal-aboutus.html", "deal-finance.html", "deal-forms.html", "deal-contact.html",
    "cust-aboutus.html", "cust-finance.html", "cust-pay.html", "cust-contact.html",
    "404.html",
]

OLD_LINK = """\
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500&display=swap&font-display=swap" rel="stylesheet">"""

NEW_LINK = '  <link rel="stylesheet" href="fonts/fonts.css">'

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8")

def fetch_binary(url, path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        with open(path, "wb") as f:
            f.write(r.read())

def main():
    os.makedirs("fonts", exist_ok=True)
    print("Fetching Google Fonts CSS...")
    css = fetch(GOOGLE_URL)

    # Extract all font URLs
    urls = re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', css)
    print(f"Found {len(urls)} font files")

    # Download each font and rewrite URLs to local paths
    local_css = css
    for url in urls:
        filename = url.split("/")[-1].split("?")[0]
        local_path = f"fonts/{filename}"
        print(f"  Downloading {filename}...")
        fetch_binary(url, local_path)
        local_css = local_css.replace(url, filename)

    # Write local fonts.css
    with open("fonts/fonts.css", "w") as f:
        f.write(local_css)
    print("Written fonts/fonts.css")

    # Update all HTML files
    for html_file in HTML_FILES:
        if not os.path.exists(html_file):
            print(f"  Skipping {html_file} (not found)")
            continue
        with open(html_file, "r") as f:
            content = f.read()
        if "fonts.googleapis.com" in content:
            content = content.replace(OLD_LINK, NEW_LINK)
            # fallback: replace any remaining google fonts link
            content = re.sub(
                r'\s*<link rel="preconnect" href="https://fonts\.googleapis\.com">\n'
                r'\s*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\n'
                r'\s*<link href="https://fonts\.googleapis\.com[^"]*" rel="stylesheet">',
                f'\n{NEW_LINK}',
                content
            )
            with open(html_file, "w") as f:
                f.write(content)
            print(f"  Updated {html_file}")
        else:
            print(f"  Already updated: {html_file}")

    print("\nDone! Commit and push the fonts/ folder + updated HTML files.")
    print("git add fonts/ *.html && git commit -m 'Self-host fonts for performance' && git push")

if __name__ == "__main__":
    main()

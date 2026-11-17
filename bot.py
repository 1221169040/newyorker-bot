import os
import requests
from bs4 import BeautifulSoup

SENT_FILE = "sent.txt"


def get_sent_links():
  if not os.path.exists(SENT_FILE):
    return set()
  with open(SENT_FILE, "r") as f:
    return set(line.strip() for line in f if line.strip())


def save_sent_link(link):
  with open(SENT_FILE, "a") as f:
    f.write(link + "\n")


def get_next_unread_essay(sent_links):
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  # Check page 1 first, then dig deeper into archive pages (page/2, page/3, etc.)
  for page in range(1, 25):
    url = (
        "https://www.newyorker.com/culture/personal-history"
        if page == 1
        else f"https://www.newyorker.com/culture/personal-history/page/{page}"
    )

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      break

    soup = BeautifulSoup(response.text, "html.parser")

    for a in soup.find_all("a", href=True):
      href = a["href"]
      if (
          "/culture/personal-history/" in href
          and "/page/" not in href
          and href != "/culture/personal-history"
      ):
        if href.startswith("/"):
          href = "https://www.newyorker.com" + href
        # Strip any tracking query parameters so URLs match cleanly
        href = href.split("?")[0]

        if href not in sent_links:
          return href

  raise Exception("No unread personal history essays found!")


def send_to_discord(webhook_url, article_url):
  payload = {
      "content": (
          "📖 **Your Daily New Yorker Personal History Essay:**\n"
          f"{article_url}"
      )
  }
  response = requests.post(webhook_url, json=payload)
  if response.status_code not in [200, 204]:
    raise Exception(f"Failed to send to Discord: {response.status_code}")


if __name__ == "__main__":
  webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
  if not webhook_url:
    raise Exception("DISCORD_WEBHOOK_URL environment variable not set.")

  sent_links = get_sent_links()
  next_essay = get_next_unread_essay(sent_links)

  print(f"Sending essay: {next_essay}")
  send_to_discord(webhook_url, next_essay)
  save_sent_link(next_essay)

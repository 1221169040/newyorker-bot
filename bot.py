import os
import requests
from bs4 import BeautifulSoup


def get_latest_personal_history():
  url = "https://www.newyorker.com/culture/personal-history"
  # Include a standard User-Agent header to prevent blocking
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  response = requests.get(url, headers=headers)
  if response.status_code != 200:
    raise Exception(f"Failed to fetch page, status code: {response.status_code}")

  soup = BeautifulSoup(response.text, "html.parser")

  # Extract links belonging to the personal history section
  article_links = []
  for a in soup.find_all("a", href=True):
    href = a["href"]
    if (
        "/culture/personal-history/" in href
        and href != "/culture/personal-history"
    ):
      if href.startswith("/"):
        href = "https://www.newyorker.com" + href
      if href not in article_links:
        article_links.append(href)

  if not article_links:
    raise Exception("No personal history essays found.")

  # The first link is typically the newest entry
  return article_links[0]


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

  latest_essay = get_latest_personal_history()
  print(f"Found latest essay: {latest_essay}")
  send_to_discord(webhook_url, latest_essay)

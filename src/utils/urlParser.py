import httpx
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class UrlParser:
	def __init__(self):
		pass

	def get_pattern_name(self, url):
		path = urlparse(url).path
		parts = path.strip("/").split("/")
		if len(parts) >= 3:
			return parts[2]
		return None

	async def get_pattern_id(self, url):
		async with httpx.AsyncClient() as client:
			response = await client.get(url)
			response.raise_for_status()

		soup = BeautifulSoup(response.text, "lxml")
		elem = soup.find("div", attrs={"data-pattern-id": True})

		return elem["data-pattern-id"]
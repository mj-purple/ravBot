import os
import httpx
from datetime import datetime, timezone
from ravelpy import RavelryClient
from ravelpy.oauth import OAuthClient, OAuthScope
from utils import Encryption

class RavelryHandler:
	def __init__(self):
		self.crypt = Encryption()
		self.client_id = os.environ["RAVELRY_CLIENT_ID"]
		self.client_secret = os.environ["RAVELRY_SECRET"]
		self.oauth = OAuthClient(
			client_id=self.client_id,
			client_secret=self.client_secret,
			redirect_uri=os.environ["REDIRECT_URI"])
		self.client = RavelryClient(
			self.client_id,
			self.client_secret)

	def get_auth_url(self):
		return self.oauth.auth_url(scopes=[OAuthScope.OFFLINE])

	def exchange_code(self, code):
		return self.oauth.exchange_code(code=code)

	def create_client_auth(self, token):
		return RavelryClient.from_oauth_token(token)

	async def refresh_user_token(self, user):
		refresh_token = self.crypt.decrypt(user["rav_refresh_token"])
		token_expiration_date = datetime.fromisoformat(user["expiration_date"])
		if datetime.now(timezone.utc) >= token_expiration_date:
			return await self.oauth.refresh(refresh_token)
		return None
	
	async def add_favorite(self, access_token, username, pattern_id):
		decrypted_token = self.crypt.decrypt(access_token)

		url = f"https://api.ravelry.com/people/{username}/favorites/create.json"

		headers = {
			"Authorization": f"Bearer {decrypted_token}",
			"Accept": "application/json",
			"Content-Type": "application/json",
		}

		data = {
			"type": "pattern",
			"favorited_id": int(pattern_id),
			"comment": "Created with RavBot"
		}

		async with httpx.AsyncClient() as client:
			response = await client.post(
				url,
				headers=headers,
				json=data
			)

			print("STATUS:", response.status_code)
			print("BODY:", response.text)

			response.raise_for_status()

			return response.json()

	async def remove_favorite(self, access_token, username, bookmark_id):
		decrypted_token = self.crypt.decrypt(access_token)

		url = f"https://api.ravelry.com/people/{username}/favorites/{bookmark_id}.json"

		headers = {
			"Authorization": f"Bearer {decrypted_token}",
			"Accept": "application/json",
			"Content-Type": "application/json",
		}
		
		async with httpx.AsyncClient() as client:
			response = await client.delete(
				url,
				headers=headers
			)

			print("STATUS:", response.status_code)
			print("BODY:", response.text)

			response.raise_for_status()

			return response.json()
		

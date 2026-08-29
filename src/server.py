import httpx
from fastapi import Request
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from api import RavelryHandler
from db import DbHandler

app = FastAPI()
rav = RavelryHandler()
db = DbHandler()

@app.get("/ravelry/callback")
async def ravelry_callback(request: Request, code: str, state: str):
	print("========== CALLBACK START ==========")

	user = db.get_user_id_from_state(state)
	if user is None:
		return {"error": "Invalid OAuth state"}

	try:
		token = await rav.exchange_code(code)

		async with rav.create_client_auth(token.access_token) as client:
			data, etag, raw = await client.people.me()
			username = raw["user"]["username"]
			print(username)
		print(vars(token))
		db.insert_user(user, username, token)

		db.delete_oauth_state(state)

		return RedirectResponse("/ravelry/success")
	except httpx.HTTPStatusError as e:
		print("STATUS:", e.response.status_code)
		print("RESPONSE:", e.response.text)
		raise

@app.get("/ravelry/success")
async def ravelry_success():
	return HTMLResponse("""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Ravelry connected</title>
        </head>
        <body>
            <h1>Ravelry successfully connected!</h1>
            <p>You can close this tab and return to Discord.</p>
        </body>
    </html>
    """)
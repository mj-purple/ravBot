import discord
from discord.ext import commands
import os, asyncio
import uvicorn
from db import DbHandler
from server import app

token = os.environ["DISCORD_TOKEN"]
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
	try:
		synced = await bot.tree.sync()
		print(f"Commands in sync: {len(synced)}")
		for command in synced:
			print(f"  - {command.name}")
	except Exception as e:
		print(e)

async def load_cogs():
	for filename in os.listdir("./src/cogs"):
		if filename.endswith(".py"):
			await bot.load_extension(f"cogs.{filename[:-3]}")

async def start_server():
    port = int(os.getenv("SERVER_PORT", 8000))

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port
    )

    server = uvicorn.Server(config)

    await server.serve()

async def main():
	db = DbHandler()
	db.init_table()

	async with bot:
		await load_cogs()
		await asyncio.gather(
			bot.start(token),
			start_server()
		)

asyncio.run(main())
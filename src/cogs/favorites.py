import inspect
import discord
from discord import app_commands
from discord.ext import commands
from db import DbHandler
from api import RavelryHandler
from utils import UrlParser

class Favorites(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.db = DbHandler()
		self.rav = RavelryHandler()
		self.util = UrlParser()
		self.emojiDefault = "🧶"
	
	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		if "ravelry.com/patterns/library" in message.content:
			pattern_id = await self.util.get_pattern_id(message.content)

			self.db.insert_pattern(message.id, pattern_id)

			emoji = self.db.get_emoji_for_favorite()
			if emoji is None:
				emoji = self.emojiDefault
			await message.add_reaction(emoji)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):

		if payload.member and payload.member.bot or str(payload.emoji) != self.emoji:
			return

		pattern = self.db.get_pattern_from_message(payload.message_id)
		if pattern is None:
			return
		pattern_id = pattern[1]

		channel = self.bot.get_channel(payload.channel_id)

		user_id = payload.user_id
		user = self.db.get_user_from_discord_id(user_id)

		if user is None:
			await channel.send("User not registered")
			return

		username = user[1]
		user_token = user[2]

		result = await self.rav.add_favorite(user_token, username, pattern_id)

		self.db.insert_pattern_bookmark_id(user_id, pattern_id, result["bookmark"]["id"])
		print(result)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):

		if payload.member and payload.member.bot or str(payload.emoji) != self.emoji:
			return

		pattern = self.db.get_pattern_from_message(payload.message_id)
		if pattern is None:
			return
		pattern_id = pattern[1]

		channel = self.bot.get_channel(payload.channel_id)

		user_id = payload.user_id
		user = self.db.get_user_from_discord_id(user_id)

		if user is None:
			await channel.send("User not registered")
			return

		username = user[1]
		user_token = user[2]

		bookmark = self.db.get_bookmark_from_user_pattern(user_id, pattern_id)
		if bookmark is None:
			return
		
		result = await self.rav.remove_favorite(user_token, username, bookmark)
		print(result)

async def setup(bot):
    await bot.add_cog(Favorites(bot))
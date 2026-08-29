import discord
from discord import app_commands
from discord.ext import commands
from db import DbHandler
from api import RavelryHandler

class Commands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.db = DbHandler()
		self.rav = RavelryHandler()

	@app_commands.command(name="set_emoji_fav", description="Set a custom emoji for the favorite reaction")
	async def set_emoji_fav(self, interaction: discord.Interaction, emoji: str):
		emoji_current = self.db.get_emoji_for_favorite()
		if emoji_current != emoji:
			self.db.insert_emoji_favorite(emoji)
			await interaction.response.send_message(f'{emoji} has been set as the "Favorite" emoji!')
			return
		await interaction.response.send_message(f'{emoji} is already set as the "Favorite" emoji!')
	
	@app_commands.command(name="connect", description="Connect your Ravelry account")
	async def connect_ravelry(self, interaction: discord.Interaction):
		user = self.db.get_user_from_discord_id(interaction.user.id)
		if user is None:
			url, state = self.rav.get_auth_url()
			self.db.insert_oauth_state(state, interaction.user.id)

			embed = discord.Embed(
				title="Ravelry login",
				url=url,
				description="Click here and login into your account",
				color=discord.Color.blue()
			)
			await interaction.response.send_message(embed=embed)
			return

		await interaction.response.send_message("Your Ravelry account has already been connected")

async def setup(bot):
    await bot.add_cog(Commands(bot))
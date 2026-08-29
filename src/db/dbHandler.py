from pathlib import Path
import sqlite3

DATABASE_FILE = Path(__file__).resolve().parent / "data.sqlite"

class DbHandler:
	def __init__(self):
		self.con = sqlite3.connect(DATABASE_FILE)
		self.cur = self.con.cursor()

	# Custom emoji (1 -> favorite)
	def insert_emoji_favorite(self, emoji_code):
		self.cur.execute("INSERT INTO emojis VALUES (1, ?) ON CONFLICT(type) DO UPDATE SET emoji_code = excluded.emoji_code", (emoji_code,))
		self.con.commit()
	
	def get_emoji_for_favorite(self):
		self.cur.execute("SELECT emoji_code FROM emojis WHERE type = 1")
		result = self.cur.fetchone()

		return result[0] if result else None

	# User
	def insert_user(self, discord_user_id, username, rav_token):
		self.cur.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (discord_user_id, username, rav_token.access_token, rav_token.refresh_token))
		self.con.commit()

	def get_user_from_discord_id(self, discord_user_id):
		self.cur.execute("SELECT * FROM users WHERE user_id = ?", (discord_user_id,))
		result = self.cur.fetchone()

		return result if result else None

	# oAuth
	def insert_oauth_state(self, state, discord_user_id):
		self.cur.execute("INSERT INTO oauth_data (state, user_id) VALUES (?, ?)", (state, discord_user_id))
		self.con.commit()
	
	def get_user_id_from_state(self, state):
		self.cur.execute("SELECT user_id FROM oauth_data WHERE state = ?", (state,))
		result = self.cur.fetchone()
		return result[0] if result else None

	def delete_oauth_state(self, state):
		self.cur.execute("DELETE FROM oauth_data WHERE state = ?", (state,))
		self.con.commit()

	# Patterns
	def insert_pattern(self, message_id, pattern_id):
		self.cur.execute("INSERT INTO patterns (message_id, pattern_id) VALUES (?, ?)", (message_id, pattern_id))
		self.con.commit()

	def get_pattern_from_message(self, message_id):
		self.cur.execute("SELECT * FROM patterns WHERE message_id = ?", (message_id,))
		result = self.cur.fetchone()
		return result if result else None

	def insert_pattern_bookmark_id(self, discord_user_id, pattern_id, bookmark_id):
		self.cur.execute("INSERT INTO patterns_users (user_id, pattern_id, bookmark_id) VALUES (?, ?, ?)", (discord_user_id, pattern_id, bookmark_id))
		self.con.commit()

	def get_bookmark_from_user_pattern(self, discord_user_id, pattern_id):
		self.cur.execute("SELECT bookmark_id FROM patterns_users WHERE user_id = ? AND pattern_id = ?", (discord_user_id, pattern_id))
		result = self.cur.fetchone()
		return result[0] if result else None

	def init_table(self):
		self.cur.execute("CREATE TABLE IF NOT EXISTS emojis (type INTEGER PRIMARY KEY, emoji_code TEXT)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, rav_name TEXT, rav_token TEXT, rav_refresh_token TEXT)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS oauth_data (state TEXT PRIMARY KEY, user_id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(user_id))")
		self.cur.execute("CREATE TABLE IF NOT EXISTS patterns (message_id INTEGER PRIMARY KEY, pattern_id INTEGER UNIQUE)")
		self.cur.execute("CREATE TABLE IF NOT EXISTS patterns_users (user_id INTEGER, pattern_id INTEGER, bookmark_id INTEGER, PRIMARY KEY(user_id, pattern_id), FOREIGN KEY (user_id) REFERENCES users(user_id), FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id))")
		self.con.commit()
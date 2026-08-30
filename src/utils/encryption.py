import os
from cryptography.fernet import Fernet

class Encryption:
	def __init__(self):
		key = os.environ["ENCRYPTION_KEY"].encode()
		self.fernet = Fernet(key)

	def encrypt(self, value):
		return self.fernet.encrypt(value.encode()).decode()

	def decrypt(self, value):
		return self.fernet.decrypt(value.encode()).decode()
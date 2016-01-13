class Authenticator:

	def __init__(self, username, password = None, email = None):
		self.username = username
		self.password = password
		self.email = email
		self.error = None

	def checkUnique(self, entry, field):
		"""
		TODO: EDIT THIS COMMENTED LINE TO QUERY TRACKR API AS OPOSSED TO HAVING A DIRECT TIE TO THE DATABASE
		"""
		#exists = User.objects.filter(**{field : entry})
		if exists:
			return False
		else:
			return True

	def existingUser(self, username, email):
		if not self.checkUnique(username, "username") and not self.checkUnique(email, "email"):
			return True
		else:
			return False

	def existingUsername(self, username):
		if not self.checkUnique(username, "username"):
			return True
		else:
			return False

	def validForm(self):
		if self.existingUser(self.username, self.email):
			self.error = "It appears you already registered before!"
			return False
		if self.checkUnique(self.username, "username"):
			self.error = "This username is taken. Please try a new one"
			return False
		if self.checkUnique(self.email, "email"):
			self.error = "This email was already registed with. Please login with the account you have!"
			return False
		return True

	def validLogin(self):
		"""
		TODO: EDIT THIS COMMENTED LINE TO QUERY TRACKR API AS OPOSSED TO HAVING A DIRECT TIE TO THE DATABASE
		"""
		#real_user = User.objects.filter(**{"username" : self.username, "password" : self.password})
		if real_user:
			return True
		else:
			if self.existingUsername(self.username):
				self.error = "Incorrect password. Try again!"
				return False
			else:
				self.error = "Account name unrecognized. Try again!"
				return False

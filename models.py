class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email


class Post:
    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id


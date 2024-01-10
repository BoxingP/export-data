from utils.config import config


class User(object):
    def __init__(self):
        self.users = config.USERS

    def get_user(self, name):
        try:
            return next(user for user in self.users if user['name'] == name)
        except StopIteration:
            print(f'\n User {name} is not defined, enter a valid user.\n')

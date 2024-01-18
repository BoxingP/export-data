from utils.config import config
from utils.logger import Logger


class User(object):
    def __init__(self):
        self.users = config.USERS

    def get_user(self, name):
        try:
            return next(user for user in self.users if user['name'] == name)
        except StopIteration:
            error_info = f'* User {name} is not defined, enter a valid user.'
            Logger().error(error_info)
            raise StopIteration(error_info)

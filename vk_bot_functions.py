from vk_api.keyboard import VkKeyboard
from db.database import DataBaseConnection


class MyBotFunctions():

    def __init__(self, token, user_token) -> None:
        self.vk = VkApi(token=token)
        self.user_vk = VkApi(token=user_token) # не все методы работают с GROUP_TOKEN
        self.longpoll = VkLongPoll(self.vk)
        self.db = DataBaseConnection()

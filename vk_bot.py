from random import randrange
from db.datebase import DataBaseConnection
from config import GROUP_TOKEN
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from keyboards import bot_keyboard
from vk_api.keyboard import VkKeyboard

class MyBot():

    def __init__(self, token) -> None:
        self.vk = VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk)
        self.db = DataBaseConnection()
    
    def write_msg(self, user_id: int, message: str, keyboard: VkKeyboard=None) -> None:
        params = {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)}
        if keyboard is not None:
            params['keyboard'] = keyboard.get_keyboard()
        self.vk.method('messages.send', params)

    def register_user(self, user_id: int) -> None:
        fields_to_get = ['city', 'sex', 'bdate']
        response = self.vk.method('users.get', {'user_id': user_id, 'fields': ', '.join(fields_to_get)})[0]
        id = int(response['id'])
        city_id = int(response['city']['id'])
        sex_id = int(response['sex'])   
        self.db.register_user(id, city_id, sex_id)

    def event_to_me_handler(self, event)-> None: 
        request = event.text.lower()
        if request == "start":
            if not self.db.is_user_registered(event.user_id):
                self.register_user(event.user_id)
                self.write_msg(event.user_id, 'Вы зарегистрированы')
            else:
                self.write_msg(event.user_id, 'Вы уже зарегистрированы')

        elif request == "привет":
            self.write_msg(event.user_id, f"Хай, {event.user_id}")

        elif request == "пока":
            self.write_msg(event.user_id, "Пока((")

        else:
            self.write_msg(event.user_id, "Не поняла вашего ответа...")


    def start_listen(self) -> None:    
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    self.event_to_me_handler(event)
                   


if __name__ == '__main__':
    bot = MyBot(GROUP_TOKEN)
  
    bot.start_listen()
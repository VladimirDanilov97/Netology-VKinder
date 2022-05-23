from random import randrange
from db.database import DataBaseConnection
from config import GROUP_TOKEN, USER_TOKEN
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from keyboards import bot_keyboard
from vk_api.keyboard import VkKeyboard

class MyBot():

    def __init__(self, token, user_token) -> None:
        self.vk = VkApi(token=token)
        self.user_vk = VkApi(token=user_token) # не все методы работают с GROUP_TOKEN
        self.longpoll = VkLongPoll(self.vk)
        self.db = DataBaseConnection()

    def write_msg(self, user_id: int, message: str, keyboard: VkKeyboard=None) -> None:
        params = {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)}
        if keyboard is not None:
            params['keyboard'] = keyboard.get_keyboard()
        self.vk.method('messages.send', params)

    def find_city(self, query):
        params = {'q': query, 'country_id': 1}
        response = self.user_vk.method('database.getCities', params)
        print(response)
        return response['items'][:10]

    def register_user(self, user_id: int) -> None:
        fields_to_get = ['city', 'sex', 'bdate']
        response = self.vk.method('users.get',
                                 {'user_id': user_id,
                                  'fields': ', '.join(fields_to_get)
                                  })[0]
        id = int(response['id'])
        city_id = int(response['city']['id'])
        sex_id = int(response['sex'])   
        self.db.register_user(id, city_id, sex_id)

    def user_command_handler(self, event)-> None: 
        request = event.text.lower()
        print(request)
        if request == "start":
            if self.db.is_user_registered(event.user_id):
                self.write_msg(event.user_id, 'Вы уже зарегистрированы', bot_keyboard)
            else:
                self.register_user(event.user_id)
                self.write_msg(event.user_id, 'Вы зарегистрированы', bot_keyboard)
               
        elif request == 'найти id города':
            new_state = 'найти id города'
            self.db.update_user_state(event.user_id, new_state=new_state)
            self.write_msg(event.user_id, 'Введите название города')
            
        else:
            self.write_msg(event.user_id, "Не поняла вашего ответа...")

    def find_city_id_command_handler(self, event):
        request = event.text.lower()
        response = self.find_city(request)
        if response:
            msg_text = 'По запросу найдено:\n'
            for city in response:
                msg_text += f"id: {city.get('id', '-')}; \
                              Город: {city.get('title', '-')}; \
                              Район: {city.get('area', '-')}; \
                              Регион: {city.get('region', '-')}\n"
            self.write_msg(event.user_id, msg_text)
        else:
            self.write_msg(event.user_id, 'Ничего не найдено')

    def start_listen(self) -> None:     
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    user_state = self.db.get_user_state(event.user_id)

                    if user_state == 'None':
                        self.user_command_handler(event)
                    elif user_state == 'найти id города':
                        self.find_city_id_command_handler(event)
                        new_state = 'None'
                        self.db.update_user_state(event.user_id, new_state)

if __name__ == '__main__':
    bot = MyBot(GROUP_TOKEN, USER_TOKEN)
  
    bot.find_city('cvxc')
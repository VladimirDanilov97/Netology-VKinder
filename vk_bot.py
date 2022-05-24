import re
import logging
from pprint import pprint
from config import GROUP_TOKEN, USER_TOKEN
from vk_api.longpoll import VkEventType
from keyboards import bot_keyboard, search_option_keyboard
from vk_bot_functions import MyBotFunctions

class MyBot(MyBotFunctions):

    def __init__(self, token, user_token) -> None:
        super().__init__(token, user_token)
        self.offset = {}
        self.suitable_users_gen = {}

    def search_command_handler(self, event):
        print(f'{event.text}')                                  # PRINT
        if re.match(r'\d+ \d+ \d+ \d+', event.text):
            user_search_params = event.text.split()
            city_id = int(user_search_params[0])
            sex_id = int(user_search_params[1])
            age_from = int(user_search_params[2])
            age_to = int(user_search_params[3])
            self.offset[event.user_id] = 0
            self.suitable_users_gen[event.user_id] = self.find_suitable_users(city_id, sex_id, age_from, age_to, self.offset[event.user_id])
            event.text = 'следующий'
            return self.search_command_handler(event)
        
        elif event.text.lower() == 'следующий':
            try:
                user_to_send = next(self.suitable_users_gen[event.user_id])
            except StopIteration:
                self.offset[event.user_id] += 20
                self.suitable_users_gen[event.user_id] = self.find_suitable_users(city_id, sex_id, age_from, age_to, self.offset[event.user_id])
                user_to_send = next(self.suitable_users_gen[event.user_id])
            try:
                user_photo = self.get_top_3_photo(user_to_send['id']) 
            except:
                event.text = 'следующий'
                return self.search_command_handler(event) 
            message = f"{user_to_send['first_name']} {user_to_send['last_name']}\n\
                        https://vk.com/id{user_to_send['id']}"
            self.send_media(user_id=event.user_id,
                            media_owner_id=user_to_send['id'],
                            media_ids=user_photo,
                            message=message,
                            keyboard=search_option_keyboard)

        elif event.text.lower() == 'назад к меню':
            new_state = 'None'
            self.db.update_user_state(event.user_id, new_state)
            self.write_msg(event.user_id, 'Выберите команду', bot_keyboard)

    def user_command_handler(self, event)-> None: 
        request = event.text.lower()
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
        
        elif request == 'начать поиск':
            new_state = 'поиск'
            self.db.update_user_state(event.user_id, new_state=new_state)
            self.write_msg(event.user_id, 'Введите запрос в формате: "id-города" "id-пола" "возраст от" "возраст до"\
                                           Например 1 1 20 25')

        else:
            self.write_msg(event.user_id, "Не понял вашего запроса...")

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

                    if event.text.lower() == 'начать сначала':
                        new_state = 'None'
                        self.db.update_user_state(event.user_id, new_state=new_state)
                        self.write_msg(event.user_id, 'Выберите команду', bot_keyboard)
                    
                    elif user_state == 'поиск':
                        self.search_command_handler(event)

                    elif user_state == 'None':
                        self.user_command_handler(event)
                        

                  
                    

if __name__ == '__main__':
    bot = MyBot(GROUP_TOKEN, USER_TOKEN)
    pprint(bot.start_listen())
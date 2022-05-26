import re
from random import shuffle
from config import GROUP_TOKEN, USER_TOKEN
from vk_api.longpoll import VkEventType
from keyboards import bot_keyboard, search_option_keyboard
from vk_bot_functions import MyBotFunctions
from datetime import date
class MyBot(MyBotFunctions):

    def __init__(self, token, user_token) -> None:
        super().__init__(token, user_token)
     
     
        self.lists_users_to_send = {}
        self.last_search_params = {}
        self.user_search_index = {}

    def search_command_handler(self, event):

        if re.match(r'\d+ \d+ \d+ \d+', event.text):
            user_search_params = event.text.split()
            self.last_search_params[event.user_id] = {
                'city_id': int(user_search_params[0]),
                'sex_id': int(user_search_params[1]),
                'age_from': int(user_search_params[2]),
                'age_to': int(user_search_params[3])
            }
            
            for age in range(int(user_search_params[2]), int(user_search_params[3])+1):
                if self.lists_users_to_send.get(event.user_id):
                    self.lists_users_to_send[event.user_id].append(self.find_suitable_users(
                                                        self.last_search_params[event.user_id]['city_id'], 
                                                        self.last_search_params[event.user_id]['sex_id'],
                                                        age_from = age,
                                                        age_to = age
                                                        ))
                else:
                    self.lists_users_to_send[event.user_id]= self.find_suitable_users(
                                                        self.last_search_params[event.user_id]['city_id'], 
                                                        self.last_search_params[event.user_id]['sex_id'],
                                                        age_from = age,
                                                        age_to = age
                                                        )
                    self.user_search_index[event.user_id] = 0
            shuffle(self.lists_users_to_send[event.user_id])
            event.text = 'следующий'
            return self.search_command_handler(event)
        
        elif event.text.lower() == 'следующий':
            try:
                user_to_send = self.lists_users_to_send[event.user_id][self.user_search_index[event.user_id]]   
                self.user_search_index[event.user_id] += 1
            
            except StopIteration:
                new_state = 'None'
                self.db.update_user_state(event.user_id, new_state=new_state)
                self.write_msg(event.user_id, 'Больше нет пользователей подходящих по запросу', bot_keyboard)
                event.text = 'начать поиск'
                return self.user_command_handler(event)
            if not self.db.is_user_in_black_list(event.user_id, user_to_send['id']):
                try:
                    user_photo = self.get_top_3_photo(user_to_send['id']) 
                except:
                    event.text = 'следующий'
                    return self.search_command_handler(event)

                if user_to_send.get('last_seen'):
                    last_seen = date.fromtimestamp(int(user_to_send['last_seen']['time'])).strftime('%d.%m.%Y')
                    last_seen = 'Заходил в последний раз: ' + last_seen + '\n'
                else:
                    last_seen = ''

                message = f"{user_to_send['first_name']} {user_to_send['last_name']}\n{last_seen}\
                            https://vk.com/id{user_to_send['id']}"
                            
                self.send_media(user_id=event.user_id,
                                media_owner_id=user_to_send['id'],
                                media_ids=user_photo,
                                message=message,
                                keyboard=search_option_keyboard)
            else:
                event.text = 'следующий'
                return self.search_command_handler(event)

        elif event.text.lower() == 'не показывать больше':
            self.db.add_to_black_list(user_id=event.user_id, blocked_user_id=self.lists_users_to_send[event.user_id][self.user_search_index[event.user_id]-1])
            event.text = 'следующий'
            return self.search_command_handler(event)
        
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
                message = 'Вы зарегистрированы\n\
                           Если знаете id нужного города нажмите начать поиск.\n\
                           Если нет, нажмите "Найти id города" и отправьте название города следующим сообщением'
                self.write_msg(event.user_id, message, bot_keyboard)
               
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
                    
                    elif user_state == 'найти id города':
                        self.find_city_id_command_handler(event)
                        new_state = 'None'
                        self.db.update_user_state(event.user_id, new_state)
                    

if __name__ == '__main__':
    bot = MyBot(GROUP_TOKEN, USER_TOKEN)

    bot.start_listen()


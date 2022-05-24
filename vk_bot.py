from pprint import pprint
from vk_api.keyboard import VkKeyboard
from db.database import DataBaseConnection
from config import GROUP_TOKEN, USER_TOKEN
from vk_api.longpoll import VkEventType
from keyboards import bot_keyboard, search_option_keyboard
from vk_bot_functions import MyBotFunctions

class MyBot(MyBotFunctions):

    def search_command_handler(self):
        pass

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
            self.write_msg(event.user_id, "Не понял вашего ответа...")

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
                        pass

                    elif user_state == 'None':
                        self.user_command_handler(event)

                    elif user_state == 'найти id города':
                        self.find_city_id_command_handler(event)
                        new_state = 'None'
                        self.db.update_user_state(event.user_id, new_state)
                    

if __name__ == '__main__':
    bot = MyBot(GROUP_TOKEN, USER_TOKEN)
  
    pprint(bot.get_top_3_photo(1))
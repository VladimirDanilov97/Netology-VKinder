import re
from datetime import date, datetime
from config import GROUP_TOKEN, USER_TOKEN
from vk_api.longpoll import VkEventType
from vk_api.exceptions import ApiError
from vk_bot_functions import MyBotFunctions
from keyboards import bot_keyboard, search_option_keyboard, start_keyboard, search_type_keyboard


class MyBot(MyBotFunctions):

    def __init__(self, token, user_token) -> None:
        super().__init__(token, user_token)
        self.__favorite_list = {}

    def search_command_handler(self, event):

        '''Если запрос попадает под регулярное выражение метод сохраняет
           в бд параметры запроса. Если текст сообщения == "следующий" бот
           делает запрос к vk api и выводит 1 пользователя подходящего
           под запрос, если он не находится в черном списке, затем увеличивает
           offset на 1. Если текст сообщения == "в избранное" пользователь
           сохраняется в favorite_list. Eсли текст сообщения == "не показывать
           больше" пользователь сохраняется в black_list
            '''

        if re.match(r'\d+\s*\d+\s*\d+\s*', event.text):
            user_search_params = event.text.split()

            search_params = {
                'city_id': int(user_search_params[0]),
                'sex_id': int(user_search_params[1]),
                'age': int(user_search_params[2]),
            }

            self.db.update_search_params(user_id=event.user_id,
                                         city_id=search_params['city_id'],
                                         sex_id=search_params['sex_id'],
                                         age=search_params['age'])

            self.db.update_user_offset(user_id=event.user_id, new_offset=0)
            event.text = 'следующий'
            return self.search_command_handler(event)

        elif event.text.lower() == 'следующий':
            offset = self.db.get_user_offset(user_id=event.user_id)
            if offset == 1000:
                self.db.update_user_state(event.user_id, 'None')
                self.write_msg(event.user_id, 'Достигнут лимит', bot_keyboard)
                
            search_params = self.db.get_search_params(user_id=event.user_id)
            try:
                user_to_send = self.find_suitable_users(
                    search_params['city_id'],
                    search_params['sex_id'],
                    age=search_params['age'],
                    offset=offset
                    )
            except IndexError:
                self.db.update_user_offset(
                    user_id=event.user_id,
                    new_offset=offset+1)
                return self.search_command_handler(event)

            new_offset = offset + 1
            self.db.update_user_offset(
                user_id=event.user_id,
                new_offset=new_offset
                )

            if not self.db.is_user_in_black_list(
                    event.user_id,
                    user_to_send['id']
                    ):
                try:
                    user_photo = self.get_top_3_photo(user_to_send['id'])
                except ApiError:
                    event.text = 'следующий'
                    return self.search_command_handler(event)

                if user_to_send.get('last_seen'):
                    last_seen = date.fromtimestamp(
                        int(user_to_send['last_seen']['time'])
                            ).strftime('%d.%m.%Y')
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
            offset = self.db.get_user_offset(user_id=event.user_id)
            search_params = self.db.get_search_params(user_id=event.user_id)
            user_to_block = self.find_suitable_users(
                                                    search_params['city_id'],
                                                    search_params['sex_id'],
                                                    age=search_params['age'],
                                                    offset=offset-1
                                                    )
            self.db.add_to_black_list(
                user_id=int(event.user_id),
                blocked_user_id=user_to_block['id']
                )
            event.text = 'следующий'
            return self.search_command_handler(event)

        elif event.text.lower() == 'в избранное':
            offset = self.db.get_user_offset(user_id=event.user_id)
            search_params = self.db.get_search_params(user_id=event.user_id)
            user_to_save = self.find_suitable_users(
                                                    search_params['city_id'],
                                                    search_params['sex_id'],
                                                    age=search_params['age'],
                                                    offset=offset-1
                                                    )
            self.db.add_to_favorite_list(
                user_id=int(event.user_id),
                favorite_user_id=user_to_save['id']
                )
            event.text = 'следующий'
            return self.search_command_handler(event)

        elif event.text.lower() == 'назад к меню':
            new_state = 'None'
            self.db.update_user_state(event.user_id, new_state)
            self.write_msg(event.user_id, 'Выберите команду', bot_keyboard)

    def find_city_id_command_handler(self, event):

        """Метод выполняет поиска id города по запросу"""

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

    def favorite_list_command_handler(self, event):

        """Бот выводит избранных пользователей и удаляет выведенных пользователей
           из self.__favorite_list[event.user_id]"""

        if self.__favorite_list[event.user_id]:
            user_to_send = self.get_user(
                self.__favorite_list[event.user_id][0]
                )
            user_photo = self.get_top_3_photo(user_id=user_to_send['id'])
            if user_to_send.get('last_seen'):
                last_seen = date.fromtimestamp(
                    int(user_to_send['last_seen']['time'])
                    ).strftime('%d.%m.%Y')
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
            self.__favorite_list[event.user_id].pop(0)
        else:
            new_state = 'None'
            self.db.update_user_state(event.user_id, new_state)
            message = 'Список закончился'
            self.write_msg(event.user_id, message, bot_keyboard)

    def user_command_handler(self, event):

        """Метод реагирует на сообщения пользователя если его состояние == None
            Если текст сообщения:
            start - пользователеь регистрируется в БД и бот
            присылает клавиатуру с командами;
            найти id города - пользователь вводит название города
            и получает результаты поиска;
            начать поиск - состояние пользователя меняется на поиск,
            бот ожидает ввода параметров поиска;
            избранное - состояние пользователя меняется на избранное, в словарь
            __favorite_list сохраняется список избранных пользователей с ключом
            event.user_id. бот выводит сохраненных пользвателей
            """

        request = event.text.lower()

        if request == "start":
            if self.db.is_user_registered(event.user_id):
                self.write_msg(
                    event.user_id,
                    'Вы уже зарегистрированы',
                    bot_keyboard)
            else:
                self.register_user(event.user_id)
                message = '''
                    Вы зарегистрированы.\n
                    Если знаете id своего города в Vk, нажмите начать поиск.\n
                    Если нет, нажмите "Найти id города" и отправьте
                    название города следующим сообщением
                    '''
                self.write_msg(event.user_id, message, bot_keyboard)

        elif request == 'найти id города':
            new_state = 'найти id города'
            self.db.update_user_state(event.user_id, new_state=new_state)
            self.write_msg(event.user_id, 'Введите название города')

        elif request == 'начать поиск':
            self.write_msg(
                event.user_id,
                'Выберите тип поиска',
                keyboard=search_type_keyboard)

        elif request in ('быстрый поиск', "задать параметры"):
            new_state = 'поиск'

            if request == 'задать параметры':
                self.write_msg(
                    event.user_id,
                    '''
                    Введите запрос в формате: 
                    id-города\n\
                    id-пола [женcкий - 1; мужской -2]\n\
                    возраст\n\
                    Например: 1 2 25
                    ''')
                self.db.update_user_state(event.user_id, new_state=new_state)

            elif request == 'быстрый поиск':
                try:
                    user = self.get_user(event.user_id)
                    age = datetime.now().year - int(user['bdate'][-4:])
                    opposite_sex = lambda x: 1 if x == '2' else 2 if x == '1' else '1'
                    event.text = f"{user['city']['id']} {opposite_sex(user['sex'])} {age}"
                    self.db.update_user_state(event.user_id, new_state=new_state)
                    return self.search_command_handler(event)
                except KeyError:
                    self.write_msg(event.user_id,
                    'Ваш профиль закрыт, используйте настраиваемый поиск',
                    bot_keyboard
                    )
                

        elif request == 'избранное':
            favorite_users = self.db.get_favorite_list(event.user_id)
            self.__favorite_list[event.user_id] = favorite_users
            new_state = 'избранное'
            self.db.update_user_state(event.user_id, new_state=new_state)
            self.favorite_list_command_handler(event)
            
        else:
            self.write_msg(event.user_id, "Для того чтобы начать, нажмите start", start_keyboard)

    def start_listen(self) -> None:

        '''Метод проверяет сообщение текста или состояние пользователя и вызывает
           методы обработки сообщения подходящие под условия''' 

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

                    elif user_state == 'избранное':
                        self.favorite_list_command_handler(event)
                    

if __name__ == '__main__':
    bot = MyBot(GROUP_TOKEN, USER_TOKEN)
    bot.start_listen()


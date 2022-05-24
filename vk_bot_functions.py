from random import randrange
from db.database import DataBaseConnection
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType

class MyBotFunctions():

    def __init__(self, token, user_token) -> None:
        self.vk = VkApi(token=token)
        self.user_vk = VkApi(token=user_token) # не все методы работают с GROUP_TOKEN
        self.longpoll = VkLongPoll(self.vk)
        self.db = DataBaseConnection()

    def write_msg(self, user_id: int, message: str, keyboard: VkKeyboard=None) -> None:
        '''Отправляет пользователю с id=user_id сообщение с текстом message'''
        params = {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)}
        if keyboard is not None:
            params['keyboard'] = keyboard.get_keyboard()
        self.vk.method('messages.send', params)

    def find_city(self, query):
        '''Находить id города по запросу query. Возвращает первые 10 результатов'''
        params = {'q': query, 'country_id': 1}
        response = self.user_vk.method('database.getCities', params)
        return response['items'][:10]

    def register_user(self, user_id: int) -> None:
        """Добавляет id пользователя, пол и id города в таблицу users базы данных"""
        fields_to_get = ['city', 'sex', 'bdate']
        response = self.vk.method('users.get',
                                 {'user_id': user_id,
                                  'fields': ', '.join(fields_to_get)
                                  })[0]
        id = int(response['id'])
        city_id = int(response['city']['id'])
        sex_id = int(response['sex'])   
        self.db.register_user(id, city_id, sex_id)

    def find_suitable_user_ids(self, city_id, sex_id, age_from, age_to, offset=0): # выдает по 20 id за 1 запрос
        """Находит id пользователей подоходящих по указанным критериям
           city_id - id города;
           sex_id - id пола;
           age_from - возраст от;
           age_to - возраст до;"""
        params = {'city': city_id, 'sex': sex_id,
                  'age_from': age_from, 'age_to': age_to,
                  'offset': offset, 'has_photo': 1}
        response = self.user_vk.method('users.search', params)
        ids = [item['id'] for item in response['items']]
        return ids
    
    def get_photo_by_id(self, user_id):
        params = {'owner_id': user_id, 'album_id': 'profile', 'extended': 1}
        response = self.user_vk.method('photos.get', params)
        return response['items']

    def get_top_3_photo(self, user_id):
        '''Возвращает топ-3 фотографии максимального размера отсортированные по сумме лайков и комментариев'''
        photos = self.get_photo_by_id(user_id)
        sorted_photo = sorted(photos, reverse=True, key=lambda photo: int(photo['likes']['count'])+int(photo['comments']['count']))[:3]
        max_size_photo = [photo['sizes'][-1]['url'] for photo in sorted_photo]
        return max_size_photo
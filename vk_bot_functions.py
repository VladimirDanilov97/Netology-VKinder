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

    def find_suitable_users(self, city_id, sex_id, age_from, age_to, offset=0): # выдает по 20 id за 1 запрос
        """Находит id пользователей подоходящих по указанным критериям
           city_id - id города;
           sex_id - id пола;
           age_from - возраст от;
           age_to - возраст до;"""
        params = {'city': city_id, 'sex': sex_id,
                  'age_from': age_from, 'age_to': age_to,
                  'offset': offset, 'has_photo': 1,
                  'fields': 'relation', 'is_closed': 'false'}
                  
        response = self.user_vk.method('users.search', params)
        users = [item for item in response['items'] if int(item.get('relation', -1)) in (-1, 1, 6)]
        return users

    def get_top_3_photo(self, user_id):
        '''Возвращает топ-3 фотографии максимального размера отсортированные по сумме лайков и комментариев'''
        params = {'owner_id': user_id, 'album_id': 'profile', 'extended': 1}
        response = self.user_vk.method('photos.get', params)
        photos = response['items']
        sorted_photo = sorted(photos, reverse=True, key=lambda photo: int(photo['likes']['count'])+int(photo['comments']['count']))[:3]
        photo_ids = [photo['id'] for photo in sorted_photo]
        return photo_ids
    
    def send_media(self, user_id, media_owner_id, media_ids: list, message, keyboard: VkKeyboard=None, media_type='photo'):
       
        media_urls = [f'{media_type}{media_owner_id}_{media_id}' for media_id in media_ids]
        print(media_urls)
        params = {'user_id': user_id, 'message': message,
                  'attachment': ','.join(media_urls), 'random_id': randrange(10 ** 7)}
        if keyboard is not None:
            params['keyboard'] = keyboard.get_keyboard()
        self.vk.method('messages.send', params)
    

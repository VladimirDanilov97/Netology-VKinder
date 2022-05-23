from vk_bot import MyBot
from config import GROUP_TOKEN, USER_TOKEN

if __name__ == '__main__':
    bot = MyBot(GROUP_TOKEN, USER_TOKEN)  
    bot.start_listen()
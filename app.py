from vk_bot import MyBot
from config import GROUP_TOKEN

if __name__ == '__main__':
    bot = MyBot(GROUP_TOKEN)  
    bot.start_listen()
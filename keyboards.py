from click import command
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

bot_keyboard = VkKeyboard(one_time=True)
bot_keyboard.add_button('Найти id Города', VkKeyboardColor.PRIMARY)
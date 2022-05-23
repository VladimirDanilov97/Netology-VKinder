from click import command
from vk_api.keyboard import VkKeyboard, VkKeyboardButton, VkKeyboardColor

bot_keyboard = VkKeyboard()
bot_keyboard.add_button('Найти id Города', VkKeyboardColor.PRIMARY)
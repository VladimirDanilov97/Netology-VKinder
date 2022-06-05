from click import command
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


bot_keyboard = VkKeyboard(one_time=False)
bot_keyboard.add_button('Начать поиск', VkKeyboardColor.POSITIVE)
bot_keyboard.add_button('Найти id города', VkKeyboardColor.PRIMARY)
bot_keyboard.add_line()
bot_keyboard.add_button('Избранное', VkKeyboardColor.SECONDARY)
bot_keyboard.add_button('Начать сначала', VkKeyboardColor.NEGATIVE)


search_option_keyboard = VkKeyboard(one_time=False)
search_option_keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
search_option_keyboard.add_button('В избранное', VkKeyboardColor.POSITIVE)
search_option_keyboard.add_line()
search_option_keyboard.add_button('Не показывать больше', VkKeyboardColor.NEGATIVE)
search_option_keyboard.add_button('Назад к меню', VkKeyboardColor.PRIMARY)

start_keyboard = VkKeyboard(one_time=True)
start_keyboard.add_button('Start', VkKeyboardColor.PRIMARY)
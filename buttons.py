from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def main_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Подвести итоги', "Проверить статистику", 'Закончить день', "Начать день")
    return keyboard

def day_result_buttons(tasks:list, Sergey):
    keyboard = InlineKeyboardMarkup()

    for task in tasks:
        if Sergey.current_day.tasks[task] != '✔️':
            keyboard.add(InlineKeyboardButton(task, callback_data=task))

    return keyboard

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from person import PersonClass
from aiogram.utils.callback_data import CallbackData
from purposes import MainPurpose, NumericPurpose

back_btn = InlineKeyboardButton('Назад', callback_data='back')

sub_purposes_data = CallbackData('SubData', 'act', 'super_purpose', 'sub_purpose')
purpose_data = CallbackData('PData', 'act', 'purpose')
tasks_data = CallbackData('TData', 'act', 'task')

def main_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Подвести итоги', 'Что сделать?', 'Обнулить задание', "Проверить статистику", "Начать день",
        "Цели")
    return keyboard

def show_purpose(purposes):
    keyboard = InlineKeyboardMarkup()

    for purpose in purposes:
        btn = InlineKeyboardButton(purpose, callback_data=f'purpose_{purpose}')
        keyboard.add(btn)

    keyboard.add(InlineKeyboardButton("Выполненные цели", callback_data = 'completed_tasks'))
    keyboard.add(InlineKeyboardButton('Новая цель', callback_data='new_purpose'))
    
    return keyboard

def purposes_menu(purpose):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 1
    keyboard.add(
        InlineKeyboardButton('Выполнить✔️', callback_data = purpose_data.new('complete', purpose)),
        InlineKeyboardButton('Подцели', callback_data= purpose_data.new('subpurposes', purpose)),
        InlineKeyboardButton('Добавить цифровую подцель', callback_data = purpose_data.new('num_sub', purpose)),
        InlineKeyboardButton('Добавить текстовую подцель', callback_data = purpose_data.new('str_sub', purpose)),
        InlineKeyboardButton('Удалить цель', callback_data = purpose_data.new('del_purpose', purpose)),
        back_btn,
    )
    return keyboard

def subpurposes(purpose, subpurposes: list):
    keyboard = InlineKeyboardMarkup()
    print(purpose)
    for subpurpose in subpurposes:
        keyboard.add(
            InlineKeyboardButton(
                subpurpose,
                callback_data=f'sub_{purpose}_{subpurpose}'
            )
        )

    return keyboard
    

def subpurpose_menu(super_purpose, purpose):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton('Выполнить✔️', callback_data = sub_purposes_data.new('c', super_purpose, purpose)),
        InlineKeyboardButton('Удалить цель', callback_data = sub_purposes_data.new('d', super_purpose, purpose)),
        InlineKeyboardButton('Назад', callback_data = sub_purposes_data.new('b', super_purpose, purpose))
    )

    if isinstance(purpose, NumericPurpose):
        keyboard.add(
            InlineKeyboardButton('Изменить значение', callback_data=sub_purposes_data.new('cd', super_purpose, purpose))
        )

    return keyboard

def day_result_buttons(tasks:list, Person):
    keyboard = InlineKeyboardMarkup()

    for task in tasks:
        if Person.current_day.tasks[task] != '✔️':
            keyboard.add(InlineKeyboardButton(task, callback_data=task))

    return keyboard

def uncompleted_tasks_buttons(tasks:list):
    keyboard = InlineKeyboardMarkup()

    for task in tasks:
        keyboard.add(InlineKeyboardButton(task, callback_data = tasks_data.new('uncomp', task)))

    return keyboard

def del_tasks_buttons(Person:PersonClass):
    keyboard = InlineKeyboardMarkup()

    for task in Person.tasks:
        keyboard.add(InlineKeyboardButton(task,callback_data = tasks_data.new('del', task)))

    return keyboard

def td_del_tasks_buttons(Person:PersonClass):
    keyboard = InlineKeyboardMarkup()

    for task in Person.current_day.tasks:
        keyboard.add(InlineKeyboardButton(task, callback_data=tasks_data.new('td_del', task)))

    return keyboard

def recommend_another(tasks):
    keyboard = InlineKeyboardMarkup()
    if len(tasks) != 0:
        keyboard.add(InlineKeyboardButton('Посоветуй что нибудь кроме этого', callback_data='recommend_another'))
    return keyboard

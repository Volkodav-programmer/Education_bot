from email import message
from aiogram import Bot, Dispatcher, executor, types, utils
from buttons import main_buttons, day_result_buttons
from tasks import pack, unpack, SergeyClass
from datetime import datetime
import shelve

TOKEN = '5269150721:AAFUSuiy9_LOSar6Ab3Ce9J7DWAiQGsaXrc'

bot = Bot(TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def greet_sergey(message:types.Message):
    if 'Sergey' not in shelve.open('user/' + str(message.from_user.id)):
        pack(str(message.from_user.id), 'Sergey', SergeyClass())
    print(message.from_user.full_name)
    await message.answer('Привет, Серег.\nВ курс дела тебя вводить не придется, что хочешь сделать?', reply_markup=main_buttons())

@dp.message_handler(commands=['help'])
async def assist(message:types.Message):
    help_text = 'Бот, который помогает Сергеям наконец то взятся за ум \
и хранить статистику по дням.\nС момента запуска день уже начался, так что тыкай на кнопку "подвести итоги", и смотри дальше по функционалу.\n\
После того как тыкнешь "закончить день", появится статистика о первом дне!\n\nКороче, проверяй)'
    await message.answer(help_text)

@dp.message_handler(commands=['new_sergey'])
async def new_Sergey(message:types.Message):
    await message.answer('Хитрюга)')
    pack(str(message.from_user.id), 'Sergey', SergeyClass())
    await message.answer('Новый Сергей успешно создан')

@dp.message_handler(content_types=['text'])
async def Education_bot(message:types.Message):
    text = message.text
    sergey_id = str(message.from_user.id)
    Sergey = unpack(sergey_id, 'Sergey')

    if text == 'Начать день':
        await start_Sergeys_day(message, Sergey)

    elif text == 'Подвести итоги':
        await Sergey_day_results(message, Sergey)

    elif text == 'Проверить статистику':
        await show_Sergey_results(message, Sergey)
    
    elif text == 'Закончить день':
        await end_Sergeys_day(message, Sergey)

    pack(sergey_id, 'Sergey', Sergey)

@dp.callback_query_handler(lambda x: x.data in unpack(str(x.from_user.id), 'Sergey').tasks)
async def day_result(callback:types.CallbackQuery):
    Sergey = unpack(str(callback.from_user.id), 'Sergey')

    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, Sergey.current_day.complete_task(callback.data))
    
    pack(str(callback.from_user.id), 'Sergey', Sergey)

async def start_Sergeys_day(message:types.Message, Sergey:SergeyClass):
    if datetime.now().strftime('%d.%m.%Y') != Sergey.current_day.date:
        Sergey.start_day()
        await message.answer('Утречка)')
    else:
        await message.answer('Дай прошлому дню закончится, дуреха :)')


async def Sergey_day_results(message:types.Message, Sergey:SergeyClass):
    tasks = Sergey.current_day.tasks
    if list(tasks.values()).count('✖️') != 0:
        await bot.send_message(message.from_user.id, 'Да, ну и что ты за сегодня сделал?', reply_markup=day_result_buttons(list(Sergey.current_day.tasks.keys()), Sergey))
    else:
        await message.answer('Ну ты вроде все сегодня сделал(а), можешь пойти и обнять кого нибудь))')

async def show_Sergey_results(message:types.Message, Sergey:SergeyClass):
    await message.answer(Sergey.show_stat())

async def end_Sergeys_day(message:types.Message, Sergey:SergeyClass):

    if not Sergey.current_day.is_ended:
        Sergey.end_day()
    else:
        await message.answer('Да понял, я, понял, не повторяйся(', reply_markup=main_buttons())
        return

    await message.answer('Хороший был денек...')
    pack(str(message.from_user.id), 'Sergey', Sergey)

try:
    executor.start_polling(dp, skip_updates=True)
except utils.exceptions.NetworkError:
    print("Low connection")
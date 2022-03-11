from email import message
import re
from aiogram import Bot, Dispatcher, executor, types, utils
from buttons import main_buttons, day_result_buttons
from tasks import pack, unpack, SergeyClass
from config import TOKEN
from datetime import datetime
import shelve


bot = Bot(TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def greet_sergey(message:types.Message):
    if 'Sergey' not in shelve.open('user/' + str(message.from_user.id)):
        pack(str(message.from_user.id), 'Sergey', SergeyClass())
    await message.answer('Привет, Серег.\nВ курс дела тебя вводить не придется, что хочешь сделать?', reply_markup=main_buttons())

@dp.message_handler(commands=['help'])
async def assist(message:types.Message):
    help_text = '''Здраствуйте, я ваш личный бот-журнал.
Я помогу вам следить за своими делами на протяжении своей работы.
Для того, что бы добавить задание, введите:
/add_task "Задание"
Если вы хотите дать задание только на сегодня, пропишите: 
/add_td_task "Задание".
Приятного пользования!)'''
    await message.answer(help_text)

@dp.message_handler(commands=['add_task'])
async def create_task(message:types.Message):
    task = ' '.join(message.text.split()[1:])

    if not task:
        await message.answer('Предлагаю добавить название задания😌')
        return

    user = str(message.from_user.id)
    Sergey = unpack(user, 'Sergey')

    if task in Sergey.tasks:
        await message.answer('Такое задание уже существует')
        return

    msg = Sergey.new_task(task)
    await message.answer(msg)
    pack(user, 'Sergey', Sergey)

@dp.message_handler(commands=['add_td_task'])
async def create_td_task(message:types.Message):
    task = ' '.join(message.text.split()[1:])

    if not task:
        await message.answer('Предлагаю добавить название задания😌')
        return

    user = str(message.from_user.id)
    Sergey = unpack(user, 'Sergey')

    if task in Sergey.current_day.tasks:
        await message.answer('Такое задание уже существует')
        return

    msg = Sergey.current_day.add_task(task)
    await message.answer(msg)
    pack(user, 'Sergey', Sergey)

@dp.message_handler(commands=['del_task'])
async def del_task(message:types.Message):
    user = str(message.from_user.id)
    Sergey = unpack(user, 'Sergey')
    msg = Sergey.delete_task(' '.join(message.text.split()[1:]))
    await message.answer(msg)
    pack(user, 'Sergey', Sergey)
    
@dp.message_handler(commands=['del_td_task'])
async def del_task(message:types.Message):
    user = str(message.from_user.id)
    Sergey = unpack(user, 'Sergey')
    msg = Sergey.current_day.delete_task(' '.join(message.text.split()[1:]))
    await message.answer(msg)
    pack(user, 'Sergey', Sergey)

@dp.message_handler(commands=['new'])
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


@dp.callback_query_handler(lambda x: x.data in unpack(str(x.from_user.id), 'Sergey').current_day.tasks)
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

    if len(tasks) == 0:
        await message.answer('Может, сначала задание добавишь?)')
        return

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
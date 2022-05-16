#imports

#from email import message
import logging
from subprocess import call
from aiogram import Bot, Dispatcher, executor, types, utils
from buttons import del_tasks_buttons, main_buttons, day_result_buttons, purposes_menu, recommend_another, subpurposes, uncompleted_tasks_buttons, \
    td_del_tasks_buttons, show_purpose, subpurpose_menu, back_btn, sub_purposes_data, purpose_data, tasks_data
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from purposes import MainPurpose, NumericPurpose
from aiogram.utils.markdown import bold, italic
from aiogram_calendar import SimpleCalendar, simple_cal_callback
from tasks import pack, roll, unpack, validate_date
from person import PersonClass
from config import TOKEN
from datetime import datetime
from texts import STICKERS, MDNU
from forms import *
import shelve
import asyncio
from random import choice
import re


#loggining
logging.basicConfig(level = logging.INFO)

#Creating bot
bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
#Commands
@dp.message_handler(commands=['start'])
async def greet_Person(message:types.Message):
    print(message.from_user.full_name + ' познакомился с Мику')
    if 'Miku' not in shelve.open('user/' + str(message.from_user.id)):
        pack(str(message.from_user.id), 'Miku', PersonClass(message.from_user.full_name))
        await message.answer('Привет, меня зовут Мику, я буду помогать тебе планировать свой день и следить за твоими успехами\n\
Пропиши /help и я расскажу тебе чуть больше о себе)')
        await message.answer(f'Приятно познакомиться, {message.from_user.full_name}', reply_markup=main_buttons())
        await bot.send_sticker(message.from_user.id, STICKERS['start_Miku'])
    else:
        await message.answer('Привееееет', reply_markup=main_buttons())
        await bot.send_sticker(message.from_user.id, STICKERS['hiding_Miku'])

@dp.message_handler(commands=['help'])
async def assist(message:types.Message):
    help_text = '''Итаак, я твой личный бот-журнал.
Я помогу тебе следить за своими делами на протяжении своей работы.
Для того, что бы добавить задание, введи:
/add_task
Если ты хочешь дать задание только на сегодня, пропиши: 
/add_td_task
'''
    await message.answer(help_text)

@dp.message_handler(commands=['update'])
async def change_miku_vers(message:types.Message):
    user = str(message.from_user.id)
    Person = unpack(user, 'Miku')
    pack(user, 'Miku', PersonClass(message.from_user.full_name, tasks = Person.tasks, days = Person.days, purposes = Person.purposes))
    await message.answer('Мику обновлена до последней версии')

@dp.message_handler(commands=['add_task'])
async def ask_task_name(message:types.Message):
    await TaskForm.name.set()
    await message.answer('Введи название задания 🙃')

@dp.message_handler(state='*', commands='cancel')
async def cancel(message:types.Message, state:FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and info
    await state.finish()
    await message.answer('*Ложит журнал обратно в полку*')
    await message.answer('Ладно, в другой раз')

@dp.message_handler(state=TaskForm.name)
async def create_task(message:types.Message, state:FSMContext):
    user = str(message.from_user.id)
    Person = unpack(user, 'Miku')

    task = message.text
    if task in Person.tasks:
        await message.answer('Такое задание уже существует')
        await state.finish()
        return

    await message.answer(Person.new_task(task))
    await message.answer('Кто умница? Я умница!')
    
    if roll(33):
        await bot.send_sticker(message.from_user.id, STICKERS['happy_Miku'])

    pack(user, 'Miku', Person)
    await state.finish()

@dp.message_handler(commands=['add_td_task'])
async def ask_td_task_name(message:types.Message):
    await TdTaskForm.name.set()
    await message.answer('Введи название задания 🙃')

@dp.message_handler(state = TdTaskForm.name)
async def create_td_task(message:types.Message, state:FSMContext):
    task = message.text
    user = str(message.from_user.id)
    Person = unpack(user, 'Miku')

    if task in Person.current_day.tasks:
        await message.answer('Это задание уже записано')
        await state.finish()
        return

    await message.answer(Person.current_day.add_task(task))
    pack(user, 'Miku', Person)
    await state.finish()


@dp.message_handler(commands=['del_task'])
async def ask_del_task(message:types.Message):
    person = unpack(str(message.from_user.id), 'Miku')
    await message.answer('Выбери задание, которое хочешь удалить', reply_markup = del_tasks_buttons(person))

@dp.callback_query_handler(tasks_data.filter(act = 'del'))
async def del_task(callback_q:types.CallbackQuery, callback_data: dict):
    await bot.answer_callback_query(callback_q.id)
    task = callback_data['task']
    user = str(callback_q.from_user.id)
    person = unpack(user, 'Miku')
    await callback_q.message.answer(person.delete_task(task))
    pack(user, 'Miku', person)
    
@dp.message_handler(commands=['del_td_task'])
async def ask_del_td_task(message:types.Message):
    user = str(message.from_user.id) 
    Person = unpack(user, 'Miku')
    await message.answer('Выбери задание, которое хочешь удалить', reply_markup=td_del_tasks_buttons(Person))

@dp.callback_query_handler(tasks_data.filter(act = 'td_del'))
async def del_td_task(callback_q:types.CallbackQuery, callback_data: dict):
    task = callback_data['task']
    await bot.answer_callback_query(callback_q.id)
    user = str(callback_q.from_user.id)

    Person = unpack(user, 'Miku')    
    await callback_q.message.answer(Person.current_day.delete_task(task))
    pack(user, 'Miku', Person)


@dp.message_handler(commands=['new'])
async def new_Person(message:types.Message):
    await message.answer('Опять новый журнал заводить(')
    await asyncio.sleep(0.5)
    pack(str(message.from_user.id), 'Miku', PersonClass(name = message.from_user.full_name))
    await message.answer('Я обновила твоего пользователя')
    await bot.send_sticker(message.from_user.id, STICKERS['yo_Miku'])

@dp.message_handler(text = 'Начать день')
async def start_Persons_day(message:types.Message):
    user = str(message.from_user.id)
    Person = unpack(user, 'Miku')

    if datetime.now().strftime('%d.%m.%Y') != Person.current_day.date:
        Person.start_day()
        await message.answer('Утречка)')
        await bot.send_sticker(message.from_user.id, STICKERS['sleepy_Miku'])
    else:
        await message.answer('Дай прошлому дню закончится, дуреха :)') 
        await bot.send_sticker(message.from_user.id, STICKERS['laughing_Miku'])
    pack(user, 'Miku', Person)

@dp.message_handler(text = 'Подвести итоги')
async def Person_day_results(message:types.Message):
    user = str(message.from_user.id)
    Person = unpack(user, 'Miku')

    tasks = Person.current_day.tasks

    if len(tasks) == 0:
        await message.answer('Может, сначала задание добавишь?)')
        return

    if list(tasks.values()).count('✖️') != 0:
        await bot.send_message(message.from_user.id, 'Да, ну и что ты за сегодня сделал?', reply_markup=day_result_buttons(list(Person.current_day.tasks.keys()), Person))
    else:
        await message.answer('Ну ты вроде все сегодня сделал(а), приходи ко мне завтра')
        await bot.send_sticker(message.from_user.id, STICKERS['cute_Miku'])
    pack(user, 'Miku', Person)

@dp.message_handler(text = 'Цели')
async def show_purposes(message:types.Message):
    person = unpack(str(message.from_user.id), 'Miku')
    if person.purposes:
        await message.answer('Вот все твои текущие цели: ', reply_markup=show_purpose(person.purposes))
    else:
        await message.answer('Еще ничего не добавил? Самое время)\n/new_purpose')
    #await message.answer(person.show_purposes())
    
@dp.message_handler(text = 'Проверить статистику')
async def show_Person_results(message:types.Message):
    user = str(message.from_user.id)
    Person = unpack(user, 'Miku')
    await message.answer(Person.show_stat())
    pack(user, 'Miku', Person)

@dp.message_handler(text = 'Что сделать?')
async def random_task(message:types.Message):
    user = str(message.from_user.id)
    Person = unpack(user, 'Miku')
    await message.answer(Person.recommend_task(), reply_markup=recommend_another([key for key, val in Person.current_day.tasks.items() if val != '✔️']))
    pack(user, 'Miku', Person)

@dp.message_handler(text = 'Обнулить задание')
async def show_task_to_null(message:types.Message):
    user = str(message.from_user.id)
    Person = unpack(user, 'Miku')
    tasks = Person.current_day.tasks

    if '✔️' not in tasks.values():
        await message.answer('Нет выполненных заданий')
        return

    await message.answer(
    'Какое задание хочешь аннулировать?', 
    reply_markup = uncompleted_tasks_buttons([key for key, val in tasks.items() if val == '✔️'])
    )
    pack(user, 'Miku', Person)


@dp.message_handler(commands='new_purpose')
async def start_creating_purpose(message:types.Message, state: FSMContext):
    await message.answer('Окей, начали\n\nВведи /cancel, если хочешь отменить заполнение формы')
    await message.answer("Придумай название для своей цели")
    await PurposeForm.name.set()

    async with state.proxy() as data:
        data['purpose'] = 'MainPurpose'

@dp.callback_query_handler(lambda c: c.data == 'new_purpose')
async def creating_purpose(callback:types.CallbackQuery, state: FSMContext):
    message = callback.message
    await callback.answer()
    await start_creating_purpose(message, state)

#Correct purpose name handler
@dp.message_handler(lambda m: len(m.text) <= 20, state = PurposeForm.name)
async def write_mpurpose_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await PurposeForm.next()
    await message.answer(f'Хорошо, когда планируешь её закончить? \nИли же введи /None, если еще не знаешь', reply_markup=await SimpleCalendar().start_calendar())

#Incorrect purpose name handler
@dp.message_handler(state = PurposeForm.name)
async def answer_wrong_name(message:types.Message):
    await message.answer('У меня не помещается твое название.\nДавай что нибудь по-короче, хорошо?)')
    
#Correct date handler
@dp.callback_query_handler(simple_cal_callback.filter(), state=PurposeForm.finish_date)
async def write_mpurpose_fdate(callback_query:types.CallbackQuery, callback_data:dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)

    if selected:
        date = date.strftime("%d.%m.%Y")
        if not validate_date(date):
            await asyncio.sleep(0.5)
            await callback_query.message.edit_text('Введи дату из будущего, пожалуйста :)',
            reply_markup=await SimpleCalendar().start_calendar())
            return
        else:
            await callback_query.message.delete()
    else:
        return

    async with state.proxy() as data:
        data['finish_date'] = date

    await PurposeForm.next()
    await callback_query.message.answer('Есть, записала')
    await asyncio.sleep(0.5)
    await callback_query.message.answer('Напиши заметку или введи /empty, что бы оставить поле пустым')

@dp.message_handler(commands = 'None', state = PurposeForm.finish_date)
async def write_None_fdate(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['finish_date'] = 'неопределена'
    await PurposeForm.next()
    await message.answer('Напиши заметку или введи /empty, что бы оставить поле пустым')
#Wrong date handler
@dp.message_handler(state = PurposeForm.finish_date)
async def answe_to_wrong_date(message:types.Message):
    await message.answer('Не-не-не-не, это не дата, напиши правильно')

@dp.message_handler(state = PurposeForm.ad_text)
async def write_mpurpose_adText(message: types.Message, state: FSMContext):

    message.from_user.id
    user = str(message.from_user.id)
    person = unpack(user, 'Miku')

    val = message.text
    if val == '/empty':
        val = ''
    
    async with state.proxy() as data:
        purpose = data['purpose']
        data['ad_text'] = val

        if 'is_numeric' in data:
            await PurposeForm.next()
            await message.answer('Хорошо, введи стандартное значение твоей цифровой цели')
            return

        if purpose == 'MainPurpose':
            person.new_purpose(MainPurpose(**data))
        elif purpose in person.purposes:
            person.purposes[purpose].create_str_purpose(**data)
    
    await state.finish()
    pack(user, 'Miku', person)
    await message.answer('Я записала тебе эту цель, удачки!', reply_markup=main_buttons())
    await show_purposes(message)
    
    if roll(20):
        await bot.send_sticker(message.from_user.id, STICKERS['victory_Miku'])

@dp.message_handler(lambda m: m.text.isnumeric(), state = PurposeForm.current_val)
async def write_curr_val(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['current_val'] = int(message.text)

    await PurposeForm.next()
    await message.answer('Введи значение, к которому ты стремишься')

@dp.message_handler(lambda m: m.text.isnumeric(), state = PurposeForm.finish_val)
async def write_finish_val(message: types.Message, state: FSMContext):
    user = str(message.from_user.id)
    person = unpack(user, 'Miku')
    val = int(message.text)

    async with state.proxy() as data:

        if val <= data['current_val']:
            await message.answer('Кажется, ты ошибся\nКонечное значение не может быть меньше текущего :)')
            return

        data['finish_val'] = val
        purpose = data['purpose']
        person.purposes[purpose].create_numeric_purpose(**data)

    await state.finish()
    await message.answer('Я записала эту цель ;)')
    await show_purposes(message)
    pack(user, 'Miku', person)

#Callbacks
@dp.callback_query_handler(lambda x: x.data in unpack(str(x.from_user.id), 'Miku').current_day.tasks)
async def day_result(callback:types.CallbackQuery):
    Person = unpack(str(callback.from_user.id), 'Miku')

    await bot.answer_callback_query(callback.id)

    if Person.current_day.tasks[callback.data] == '✔️':
        await callback.answer('Ты уже выполнил это сегодня)')
        return

    await bot.send_message(callback.from_user.id, Person.complete_task(callback.data))

    if roll(20):
        await bot.send_sticker(callback.from_user.id, STICKERS[choice(['happy_Miku', 'loving_Miku', 'victory_Miku', 'cute_Miku', 'perky_Miku'])])

    pack(str(callback.from_user.id), 'Miku', Person)

@dp.callback_query_handler(lambda x: x.data.startswith('purpose_'))
async def focus_purpose(callbackQ:types.CallbackQuery):
    user = str(callbackQ.from_user.id)
    person = unpack(user, 'Miku') 
    await callbackQ.answer()
    purpose = person.purposes[callbackQ.data.split('_')[1]]
    await callbackQ.message.edit_text(person.show_purpose(purpose), reply_markup = purposes_menu(purpose), parse_mode='markdown')
    pack(user, 'Miku', person)

@dp.callback_query_handler(purpose_data.filter(act = 'complete'))
async def complete_purpose(callbackQ: types.CallbackQuery, callback_data: dict):
    user = str(callbackQ.from_user.id)
    person = unpack(user, 'Miku') 
    await callbackQ.answer()
    person.complete_purpose(callback_data['purpose'])
    await callbackQ.message.answer('*Демонстративно что-то черкает в журнале*')
    await callbackQ.message.answer('Ну вот и одной задачей меньше')
    await bot.send_sticker(callbackQ.from_user.id, STICKERS['cute_Miku'])
    pack(user, 'Miku', person)
    await back_to_purposes(callbackQ)

@dp.callback_query_handler(purpose_data.filter(act = 'str_sub'))
async def create_str_subpurpose(callbackQ: types.CallbackQuery, state: FSMContext, callback_data: dict):
    purpose = callback_data['purpose']
    await callbackQ.answer()
    await callbackQ.message.delete()
    await PurposeForm.name.set()

    async with state.proxy() as data:
        data['purpose'] = purpose

    await callbackQ.message.answer('Введи название для подцели: ')

@dp.callback_query_handler(purpose_data.filter(act = 'num_sub'))
async def start_numeric_subpurpose(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.answer()
    purpose = callback_data['purpose']
    await PurposeForm.name.set()

    async with state.proxy() as data:
        data['purpose'] = purpose
        data['is_numeric'] = True
    
    await callback.message.answer('Введи название для цифровой подцели')
    #await callback.message.answer('Я еще думаю, как это можно реализовать')
    #await bot.send_sticker(callback.from_user.id, STICKERS['mystery_Miku'])

@dp.callback_query_handler(purpose_data.filter(act = 'subpurposes'))
async def subpurposes_menu(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    person = unpack(str(callback.from_user.id), 'Miku')
    purpose = person.purposes[callback_data['purpose']]
    subpurposes_list = [name for name, purpose in purpose.subpurposes.items() if not purpose.is_finished]
    if not subpurposes_list:
        await callback.message.answer('У этой цели нет подцелей, сначала, добавь её')
        return

    await callback.message.edit_text('Выбери подцель:', reply_markup=subpurposes(callback_data['purpose'], subpurposes_list))
    
@dp.callback_query_handler(lambda c: c.data.startswith('sub_'))
async def show_subpurpose(callback: types.CallbackQuery):
    await callback.answer()
    person = unpack(str(callback.from_user.id), 'Miku')
    purposes = callback.data.split('_')
    super_purpose = person.purposes[purposes[1]]
    purpose = super_purpose.subpurposes[purposes[2]]
    text = purpose.show()
    await callback.message.edit_text(text, reply_markup=subpurpose_menu(super_purpose, purpose), parse_mode='markdown')
    
@dp.callback_query_handler(purpose_data.filter(act = 'del_purpose'))
async def delete_purpose(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    purpose = callback_data['purpose']
    user = str(callback.from_user.id)
    person = unpack(user, 'Miku')
    await callback.message.edit_text(person.delete_purpose(purpose))
    pack(user, 'Miku', person)

@dp.callback_query_handler(lambda c: c.data == 'back')
async def back_to_purposes(callback:types.CallbackQuery):
    await callback.answer()
    person = unpack(str(callback.from_user.id), 'Miku')
    if person.purposes:
        await callback.message.edit_text('Вот все твои текущие цели: ', reply_markup=show_purpose(person.purposes))
    else:
        await callback.message.edit_text('Еще ничего не добавил? Самое время)\n/new_purpose')

@dp.callback_query_handler(tasks_data.filter(act = 'uncomp'))
async def null_task(callback: types.CallbackQuery, callback_data: dict):
    u_id = callback.from_user.id
    Person = unpack(str(u_id), 'Miku')
    await callback.answer()
    Person.current_day.null_task(callback_data['task'])
    await bot.send_message(u_id, 'Я сняла метку выполненности с твоего задания')
    pack(str(u_id), 'Miku', Person)

@dp.callback_query_handler(lambda x: x.data == 'recommend_another')
async def recommend_smth(callback:types.CallbackQuery):
    u_id = callback.from_user.id
    Person = unpack(str(u_id), 'Miku')
    await callback.answer()
    await bot.send_message(u_id, Person.recommend_another())
    await bot.send_sticker(u_id, STICKERS['mystery_Miku'])
    pack(str(u_id), 'Miku', Person)

@dp.callback_query_handler(lambda c: c.data == 'completed_tasks')
async def show_completed_tasks(callback: types.CallbackQuery):
    person = unpack(str(callback.from_user.id), 'Miku')
    await callback.answer()
    await callback.message.edit_text(person.show_completed_purposes(), reply_markup=types.InlineKeyboardMarkup().add(back_btn)) 

@dp.callback_query_handler(sub_purposes_data.filter(act = 'c'))
async def complete_sub_purpose(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()

    user = str(callback.from_user.id)
    person = unpack(user, 'Miku')

    super_purpose = person.purposes[callback_data['super_purpose']]
    super_purpose.completeSub(callback_data['sub_purpose'])
    await callback.message.delete()
    await callback.message.answer('Одной подзадачей меньше!')
    await callback.message.answer(
        person.show_purpose(super_purpose), 
        parse_mode='markdown',
        reply_markup=purposes_menu(super_purpose),
    )
    
    pack(user, 'Miku', person)

@dp.callback_query_handler(sub_purposes_data.filter(act = 'd'))
async def delete_sub_purpose(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()

    user = str(callback.from_user.id)
    person = unpack(user, 'Miku')
    super_purpose = person.purposes[callback_data['super_purpose']]
    sub_purpose = callback_data['sub_purpose']

    super_purpose.delete_subpurpose(sub_purpose)
    await callback.message.edit_text('Подцель удалена')
    await callback.message.answer(person.show_purpose(super_purpose), reply_markup=purposes_menu(super_purpose),
    parse_mode='markdown')

    pack(user, 'Miku', person)

@dp.callback_query_handler(sub_purposes_data.filter(act = 'b'))
async def back_to_purpose(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()

    user = str(callback.from_user.id)
    person = unpack(user, 'Miku')
    purpose = person.purposes[callback_data['super_purpose']]

    await callback.message.edit_text(
        person.show_purpose(purpose),
        reply_markup=purposes_menu(purpose),
        parse_mode='markdown'
    )

@dp.callback_query_handler(sub_purposes_data.filter(act = 'cd'))
async def ask_numeric_purpose_data(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await callback.answer()
    await Change_valForm.current_val.set()
    await callback.message.edit_text('Введи новое значение для цели: ')
    async with state.proxy() as data:
        data['super_purpose'] = callback_data['super_purpose']
        data['sub_purpose'] = callback_data['sub_purpose']

@dp.message_handler(state = Change_valForm.current_val)
async def change_numeric_purpose_data(message: types.Message, state: FSMContext):
    user = str(message.from_user.id)
    person = unpack(user, 'Miku')

    async with state.proxy() as data:
        super_purpose = person.purposes[data['super_purpose']]
        sub_purpose = super_purpose.subpurposes[data['sub_purpose']]

    await message.answer(sub_purpose.change_current_value(int(message.text)))
    await state.finish()
    pack(user, 'Miku', person)
    await show_purposes(message)


@dp.message_handler(content_types='text')
async def Miku_does_not_understand(message:types.Message):
    await message.answer(choice(MDNU))
    if roll(20):
        await bot.send_sticker(message.from_user.id, STICKERS['upset_Miku'])

#Other funcs
async def end_Persons_day(message:types.Message, Person:PersonClass):
    if not Person.current_day.is_ended:
        Person.end_day()
    else:
        await message.answer('Да поняла, я, поняла, не повторяйся(', reply_markup=main_buttons())
        await bot.send_sticker(message.from_user.id, STICKERS['upset_Miku'])
        return

    await message.answer('Хороший был денек...')
    await bot.send_sticker(message.from_user.id, STICKERS['going_to_sleep_Miku'])
    pack(str(message.from_user.id), 'Miku', Person)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
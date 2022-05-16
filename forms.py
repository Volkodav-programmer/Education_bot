from aiogram.dispatcher.filters.state import State, StatesGroup

class TaskForm(StatesGroup):
    name = State()

class TdTaskForm(StatesGroup):
    name = State()

class PurposeForm(StatesGroup):
    name = State()
    finish_date = State()
    ad_text = State()
    current_val = State()
    finish_val = State()

class Change_valForm(StatesGroup):
    current_val = State()
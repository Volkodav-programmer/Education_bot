from calendar import month
from datetime import datetime
from icecream import ic

from random import choice, randint
from texts import CONGRATULATIONS
import shelve

class Day:
    def __init__(self, tasks) -> None:
        self.date = datetime.now().strftime('%d.%m.%Y')
        self.tasks = {x:'✖️' for x in tasks}
        self.is_ended = False

    def add_task(self, task):
        if len(task) <= 30:
            if len(self.tasks) != 13:
                self.tasks[task] = '✖️'
                msg = 'Задание на сегодня успешно добавлено'
            else:
                msg = 'Слишком много заданий. 🚬🗿'
        else:
            msg = 'Длина задания не должна превышать 30 символов'
        return msg

    def delete_task(self, task):
        self.tasks.pop(task)
        msg = 'Задание  на сегодня успешно удалено'
        return msg

    def null_task(self, task):
        self.tasks[task] = '✖️'

    def __str__(self):
        return self.date



def pack(shelve_name, key, value):
    with shelve.open(f'user/{shelve_name}') as shelf:
        shelf[key] = value

def unpack(shelve_name, key):
    with shelve.open(f'user/{shelve_name}') as shelf:
        return shelf[key]

def roll(chance):
    return randint(0, 100) < chance

def validate_date(date):
    day, month, year = [int(x) for x in date.split('.')]
    tDay, tMonth, tYear = [int(x) for x in datetime.today().strftime('%d.%m.%Y').split('.')]
    
    if tYear == year and month == tMonth and day >= tDay or month > tMonth and year == tYear or year > tYear:
        return True
    return False


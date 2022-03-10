from datetime import datetime
import shelve

class Day:
    def __init__(self, tasks) -> None:
        self.date = datetime.now().strftime('%d.%m.%Y')
        self.tasks = {x:'✖️' for x in tasks}
        self.is_ended = False

    def complete_task(self, task):
        self.tasks[task] = '✔️'
        return 'Моя ты умничка ;)'

    def add_task(self, task):
        if len(task) <= 16:
            self.tasks[task] = '✖️'
            msg = 'Задание на сегодня успешно добавлено'
        else:
            msg = 'Длина задания не должна превышать 16 символов'
        return msg

    def __str__(self):
        return self.date

class SergeyClass:

    def __init__(self) -> None:
        self.days = []
        self.tasks = []
        self.current_day = Day(self.tasks)

    def start_day(self):
        self.current_day = Day()
        
    def end_day(self):
        self.current_day.is_ended = True
        self.days.append(self.current_day)

    def new_task(self, task):
        if len(task) <= 16:
            self.tasks.append(task)
            self.current_day.add_task(task)
            msg = 'Задание успешно добавлено'
        else:
            msg = 'Длина задания не должна превышать 16 символов'
        return msg

    def show_stat(self):
        text = ''
        count = {x:0 for x in self.tasks}

        if not self.days:
            return 'Ничего ты ещё не добился;('

        for day in self.days:
            text += day.date + '\n'
            for task, value in day.tasks.items():
                
                text += f'{task} - {value}\n'
            
                if value == '✔️' and task in self.tasks:
                    count[task] += 1 
        
        for task, value in count.items():
            text += f'\n{task} - {value}✔️'

        return text

def pack(shelve_name, key, value):
    with shelve.open(f'user/{shelve_name}') as shelf:
        shelf[key] = value

def unpack(shelve_name, key):
    with shelve.open(f'user/{shelve_name}') as shelf:
        return shelf[key]
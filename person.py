from random import choice
from texts import CONGRATULATIONS
from tasks import Day, roll

class PersonClass:

    def __init__(self, name, days = [], tasks = [], purposes = {}) -> None:
        self.name = name
        self.days = days
        self.tasks = tasks
        self.purposes = purposes
        self.completed_purposes = []
        self.recommended_task = None
        self.focused_purpose= None
        self.start_day()

    def start_day(self):
        self.current_day = Day(self.tasks)
        self.recommended_task = None

        if not self.current_day.date in [x.date for x in self.days]:
            self.days.append(self.current_day)
        
    def end_day(self):
        self.current_day.is_ended = True

    def new_task(self, task):
        if len(task) <= 30:
            if len(self.tasks) != 11:
                self.tasks.append(task)
                self.current_day.tasks[task] = '✖️'
                msg = 'Я добавила новое задание'
            else:
                msg = 'Я понимаю, многозадачность и все такое, но давай чучуть уменьшим количество заданий?'
        else:
            msg = 'Длина задания не должна превышать 30 символов'
        return msg

    def show_stat(self):
        text = ''
        count = {x:0 for x in self.tasks}
        
        if len(self.days) == 1 and not self.current_day.tasks:
            text = 'Ничего ты еще не добился(ась) ;('
            return text

        for day in self.days:
            text += day.date + '\n'
            for task, value in day.tasks.items():
                text += f'{task} - {value}\n'
            
                if value == '✔️' and task in self.tasks:
                    count[task] += 1   
            text += '\n'

        for task, value in count.items():
            text += f'\n{task} - {value}✔️'

        text += f'\n\nВсего дней - {len(self.days)}'
        return text

    def delete_task(self, task):
        self.tasks.remove(task)
        self.current_day.tasks.pop(task)
        msg = 'Задание успешно удалено'
        return msg

    def complete_task(self, task):
        self.current_day.tasks[task] = '✔️'

        if task == self.recommended_task:
            self.recommended_task = None

        if list(self.current_day.tasks.values()).count('✖️'):
            return choice(CONGRATULATIONS)
        return 'Ну вот и все на сегодня)'

    def recommend_task(self):

        if not self.recommended_task:
            uncompleted_tasks = [key for key, val in self.current_day.tasks.items() if val != '✔️']

            if len(self.days) == 1 and not self.current_day.tasks:
                text = 'А из чего выбирать то? ;('
                return  text

            if len(uncompleted_tasks) == 1:
                last_task = uncompleted_tasks[0]
                return f'{last_task} или {last_task.lower()}?🤔\nБоюсь, тебе придется решать такую дилемму без меня)'

            if not uncompleted_tasks:
                return 'Заданий то и нет. Иди отдыхать)'

            self.recommended_task = choice(uncompleted_tasks)
            msg = f'{self.recommended_task}? Да, займись этим'
        else:
            msg = f'Не, так не получится\nЯ не передумаю\nВсе же {self.recommended_task.lower()})'
        return msg

    def recommend_another(self):
        uncompleted_tasks = [key for key, val in self.current_day.tasks.items() if val != '✔️' and key != self.recommended_task]
        self.recommended_task = choice(uncompleted_tasks)
        if len(uncompleted_tasks) == 0:
            return 'Извини, но тебе осталось сделать только это'
        return f'Нет?\nЛадно, если хочешь отложить это на потом...\n{self.recommended_task}? Давай хотя бы так'

    def new_purpose(self, purpose):
        self.purposes[purpose.name] = purpose

    def delete_purpose(self, purpose):
        self.purposes.pop(purpose)
        return 'Я вычеркнула эту цель из журнала'


    def show_purposes(self):
        text = ''
        for name in self.purposes:
            purpose = self.purposes[name]
            text += f'{purpose.name}\nПланируемая дата завершения: {purpose.plannedFinishDate}\nЗаметка: {purpose.ad_text}'
        return text

    def show_purpose(self, purpose):
        note = f'Заметка: {purpose.ad_text}' if purpose.ad_text else 'Заметка не была оставлена'
        text = f'*{(purpose.name)}*\n\nПланируемая дата завершения: {purpose.plannedFinishDate}\n{note}'
        if purpose.subpurposes: text += '\nПодцели:\n\n'
        for subpurpose in purpose.subpurposes.values():
            mark = '• ' if subpurpose.is_finished else '○ '
            date = subpurpose.plannedFinishDate if not subpurpose.is_finished else subpurpose.finished_date
            text += mark + subpurpose.name + ' - ' + date + '\n'
        return text

    def complete_purpose(self, purpose):
        self.purposes[purpose].complete()
        self.completed_purposes.append(self.purposes[purpose])
        self.purposes.pop(purpose)
    
                
    def show_completed_purposes(self):
        if not self.completed_purposes:
            return 'У тебя нет выполненных целей'
        
        text = 'Вот твои выполненные цели:\n'
        for purpose in self.completed_purposes:
            text += '• ' + str(purpose) + '. ' + 'Выполнено: ' + purpose.finished_date

        return text
    
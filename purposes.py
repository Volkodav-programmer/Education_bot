from datetime import datetime

class Purpose:
    def __init__(self, name, finish_date, ad_text) -> None:
        self.name = name
        self.plannedFinishDate = finish_date
        self.finished_date = None
        self.ad_text = ad_text
        self.startDate = datetime.now().strftime('%d.%m.%Y')
        self.is_finished = False

    def complete(self):
        self.finished_date = datetime.now().strftime('%d.%m.%Y')
        self.is_finished = True
    
    def show(self):
        note = f'Заметка: {self.ad_text}' if self.ad_text else 'Заметка не была оставлена'
        date = f'Планируемая дата завершения: {self.plannedFinishDate}' if not self.is_finished else  f'Дата завершения: {self.finished_date}'
        text = f'*{(self.name)}*\n\n{date}\n{note}'
        return text

    def __str__(self):
        return self.name 
        
class MainPurpose(Purpose):
    def __init__(self, name, finish_date, ad_text, **kwargs) -> None:
        super().__init__(name, finish_date, ad_text)
        self.subpurposes = {}

    def create_numeric_purpose(self, name, finish_date, ad_text, finish_val, current_val, **kwargs):
        purpose = NumericPurpose(name, finish_date, ad_text, finish_val, current_val)
        self.subpurposes[name] = purpose

    def create_str_purpose(self, name, finish_date, ad_text, **kwargs):
        purpose = Purpose(name, finish_date, ad_text)
        self.subpurposes[name] = purpose

    def delete_subpurpose(self, purpose):
        self.subpurposes.pop(purpose)

    def completeSub(self, subp):
        self.subpurposes[subp].complete()


class NumericPurpose(Purpose):
    def __init__(self, name, finish_date, ad_text, finish_val, current_val, **kwargs) -> None:
        super().__init__(name, finish_date, ad_text, **kwargs)
        self.finish_val = finish_val
        self.current_val = current_val

    def change_current_value(self, value):
        self.current_val = value

        if self.current_val >= self.finish_val:
            self.complete()
            return 'Ты выполнил эту цель\nПоздравляю)'
        return 'Я изменила текущее значение цели)'

    def show(self):
        text = super().show() + f'\n{self.current_val}/{self.finish_val}'
        return text

            
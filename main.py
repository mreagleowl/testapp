# main.py
# v0.4.10

import os
import json
from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.button import Button
from hover import HoverBehavior
from functools import partial

# Грузим конфиг
with open('config/config.json', encoding='utf-8') as cf:
    config = json.load(cf)

RESULTS_DIR = config.get('results_dir', 'results')
QUESTIONS_DIR = config.get('questions_dir', 'questions')
ADMIN_PIN = config.get('admin_pin', '1234')
BG_COLOR = config.get('background', [0.94, 0.94, 0.94, 1])
BUTTON_BG = config.get('button_bg', [0.25, 0.47, 0.77, 1])
BUTTON_TEXT = config.get('button_text', [1, 1, 1, 1])
HOVER_COLOR = config.get('hover_color', [0.85, 0.33, 0.18, 1])
HOVER_TEXT = config.get('hover_text', [0, 0.6, 0, 1])

def get_theme_files():
    return [
        f for f in os.listdir(QUESTIONS_DIR)
        if f.lower().endswith('.json')
    ]

class HoverButton(Button, HoverBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hover_color = HOVER_COLOR

    def on_enter(self):
        self.background_color = self.hover_color

    def on_leave(self):
        self.background_color = BUTTON_BG

class ThemeSelectionScreen(Screen):
    rv_data = ListProperty([])

    def on_pre_enter(self):
        files = get_theme_files()
        self.rv_data = [{
            'text': os.path.splitext(f)[0],
            'on_release': partial(self.select_theme, f),
            'cls': 'HoverButton'
        } for f in files]

    def select_theme(self, fname, *args):
        self.manager.get_screen('fio').set_theme(fname)
        self.manager.current = 'fio'

class FioInputScreen(Screen):
    selected_theme = StringProperty('')
    def set_theme(self, theme):
        self.selected_theme = theme
        self.ids.fio_input.text = ""
        self.ids.error.text = ""

    def start_test(self):
        fio = self.ids.fio_input.text.strip()
        if not fio:
            self.ids.error.text = "Поле не може бути порожнім"
            return
        test_screen = self.manager.get_screen('test')
        test_screen.start(self.selected_theme, fio)
        self.manager.current = 'test'

    def go_back(self):
        self.manager.current = 'themes'

class HoverCheckBox(BoxLayout, HoverBehavior):
    def __init__(self, text, is_checked, on_press, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=44, **kwargs)
        self.hover_color = HOVER_COLOR
        self.hover_text = HOVER_TEXT
        self.default_text = [0, 0, 1, 1]  # синий
        self.cb = CheckBox(active=is_checked, size_hint=(None, None), size=(32, 32))
        self.lbl = Label(
            text=text,
            halign='left',
            valign='middle',
            size_hint_x=1,
            color=self.default_text,
        )
        self.lbl.bind(size=lambda *x: setattr(self.lbl, 'text_size', (self.lbl.width, None)))
        self.add_widget(self.cb)
        self.add_widget(self.lbl)
        self.cb.bind(active=lambda inst, val: on_press())
        self.bind(hovered=self.update_hover)
        self.lbl.bind(on_touch_down=self.on_touch_label)
        self.cb.background_normal = ''
        self.cb.background_color = [1, 1, 1, 1]

    def on_enter(self):
        self.cb.background_color = self.hover_color
        self.lbl.color = self.hover_text

    def on_leave(self):
        self.cb.background_color = [1, 1, 1, 1]
        self.lbl.color = self.default_text

    def update_hover(self, *args):
        if self.hovered:
            self.on_enter()
        else:
            self.on_leave()

    def on_touch_label(self, instance, touch):
        if self.lbl.collide_point(*touch.pos):
            self.cb.active = not self.cb.active

class TestScreen(Screen):
    def start(self, theme_file, fio):
        self.theme_file = theme_file
        self.fio = fio
        with open(os.path.join(QUESTIONS_DIR, theme_file), encoding='utf-8') as f:
            data = json.load(f)
        questions = data['questions']
        count = data.get('count', len(questions))
        import random
        self.questions = random.sample(questions, min(count, len(questions)))
        self.answers = [[] for _ in self.questions]
        self.index = 0
        self.show_question()

    def show_question(self):
        q = self.questions[self.index]
        self.ids.question.text = f"{self.index+1}. {q['question']}"
        box = self.ids.answers_box
        box.clear_widgets()
        for i, option in enumerate(q['options']):
            checked = i in self.answers[self.index]
            def cb_action(idx=i):
                if idx in self.answers[self.index]:
                    self.answers[self.index].remove(idx)
                else:
                    self.answers[self.index].append(idx)
                self.show_question()
            hover_cb = HoverCheckBox(option, checked, cb_action)
            hover_cb.lbl.halign = 'left'
            hover_cb.lbl.valign = 'middle'
            hover_cb.lbl.text_size = (hover_cb.lbl.width, None)
            box.add_widget(hover_cb)
        # прогрессбар
        pr = self.ids.progress
        pr.value = (self.index+1)/len(self.questions)*100

    def prev(self):
        if self.index > 0:
            self.index -= 1
            self.show_question()

    def next(self):
        if self.index < len(self.questions) - 1:
            self.index += 1
            self.show_question()

    def finish(self):
        right = 0
        for ans, q in zip(self.answers, self.questions):
            if set(ans) == set(q.get('correct', [])):
                right += 1
        score = int(right/len(self.questions)*100)
        os.makedirs(RESULTS_DIR, exist_ok=True)
        with open(
            os.path.join(RESULTS_DIR, f"{datetime.now():%Y%m%d_%H%M%S}_{self.fio}.txt"),
            "w", encoding="utf-8"
        ) as f:
            f.write(f"{self.fio}\n{self.theme_file}\n{score}\n")
        self.manager.get_screen('result').set_score(score)
        self.manager.current = 'result'

class ResultScreen(Screen):
    def set_score(self, score):
        self.ids.score_label.text = f"Ваш результат: {score}%"

    def to_main(self):
        self.manager.current = 'themes'

class AdminPinScreen(Screen):
    def check_pin(self):
        pin = self.ids.pin_input.text.strip()
        if pin == ADMIN_PIN:
            self.manager.current = 'admin'
            self.ids.pin_input.text = ""
            self.ids.error_label.text = ""
        else:
            self.ids.error_label.text = "Невірний PIN!"

    def go_back(self):
        self.ids.pin_input.text = ""
        self.ids.error_label.text = ""
        self.manager.current = "themes"

from admin import AdminScreen

class KivyTestApp(App):
    BG_COLOR = BG_COLOR
    BUTTON_BG = BUTTON_BG
    BUTTON_TEXT = BUTTON_TEXT

    def build(self):
        return Builder.load_file("app.kv")

if __name__ == "__main__":
    KivyTestApp().run()

import os
import json
import random
from functools import partial
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.core.window import Window

CONFIG_PATH = os.path.join('config', 'config.json')
QUESTIONS_DIR = "questions"
RESULTS_DIR = "results"
REPORTS_DIR = "reports"

if not os.path.exists(CONFIG_PATH):
    os.makedirs('config', exist_ok=True)
    conf = {
        "admin_pin": "1234",
        "theme_color": "#e53935",
        "checkbox_color": "#e53935",
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(conf, f, ensure_ascii=False, indent=2)
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)
ADMIN_PIN = config.get("admin_pin", "1234")

class ThemeSelectionScreen(Screen):
    rv_data = ListProperty([])

    def on_enter(self):
        themes = []
        if not os.path.exists(QUESTIONS_DIR):
            os.makedirs(QUESTIONS_DIR)
        for fname in os.listdir(QUESTIONS_DIR):
            if fname.lower().endswith(".json"):
                try:
                    with open(os.path.join(QUESTIONS_DIR, fname), encoding="utf-8") as f:
                        data = json.load(f)
                        title = data.get("theme") or os.path.splitext(fname)[0]
                        themes.append({"text": title, "on_release": partial(self.choose_theme, fname)})
                except Exception as ex:
                    print(f"Ошибка чтения файла {fname}: {ex}")
        self.rv_data = themes

    def choose_theme(self, filename, *args):
        fio_screen = self.manager.get_screen("fio")
        fio_screen.selected_theme = filename
        self.manager.current = "fio"

class FioInputScreen(Screen):
    selected_theme = StringProperty("")

    def go_back(self):
        self.manager.current = "themes"

    def start_test(self):
        fio = self.ids.fio_input.text.strip()
        if not fio:
            self.ids.error.text = "ПІБ не може бути порожнім"
            return
        self.ids.error.text = ""
        test_screen = self.manager.get_screen("test")
        test_screen.start_test(self.selected_theme, fio)
        self.manager.current = "test"

class TestScreen(Screen):
    question_list = ListProperty([])
    answer_map = ListProperty([])
    question_idx = NumericProperty(0)
    fio = StringProperty("")
    selected_theme = StringProperty("")
    count = NumericProperty(0)

    def start_test(self, theme_file, fio):
        self.fio = fio
        self.selected_theme = theme_file
        self.question_idx = 0

        with open(os.path.join(QUESTIONS_DIR, theme_file), encoding="utf-8") as f:
            data = json.load(f)
            count = data.get("count", 10)
            all_questions = data.get("questions", [])
            if count > len(all_questions): count = len(all_questions)
            self.question_list = random.sample(all_questions, count)
            self.count = count

        self.answer_map = [[] for _ in self.question_list]
        self.update_question()

    def update_question(self):
        if not self.question_list:
            return
        q = self.question_list[self.question_idx]
        self.ids.question.text = f"{self.question_idx+1}. {q.get('question','')}"
        box = self.ids.answers_box
        box.clear_widgets()

        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.checkbox import CheckBox
        from kivy.uix.label import Label

        options = q.get("options", [])
        selected = set(self.answer_map[self.question_idx])
        for i, text in enumerate(options):
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=12)
            cb = CheckBox(active=i in selected, color=(0.9,0,0,1), size_hint=(None,None), size=(28,28))
            def on_cb_active(cb_instance, value, idx=i):
                if value:
                    if idx not in self.answer_map[self.question_idx]:
                        self.answer_map[self.question_idx].append(idx)
                else:
                    if idx in self.answer_map[self.question_idx]:
                        self.answer_map[self.question_idx].remove(idx)
            cb.bind(active=on_cb_active)
            lbl = Label(text=text, font_size=16, halign="left", valign="middle")
            def on_label_touch(instance, touch, check=cb):
                if instance.collide_point(*touch.pos):
                    check.active = not check.active
            lbl.bind(on_touch_down=on_label_touch)
            row.add_widget(cb)
            row.add_widget(lbl)
            box.add_widget(row)
        self.ids.progress.value = int(100*(self.question_idx+1)/self.count)

    def next(self):
        if self.question_idx < self.count - 1:
            self.question_idx += 1
            self.update_question()

    def prev(self):
        if self.question_idx > 0:
            self.question_idx -= 1
            self.update_question()

    def finish(self):
        filename = f"{self.fio}_{self.selected_theme}_{self.count}_{random.randint(1000,9999)}.json"
        if not os.path.exists(RESULTS_DIR): os.makedirs(RESULTS_DIR)
        with open(os.path.join(RESULTS_DIR, filename), "w", encoding="utf-8") as f:
            json.dump({
                "fio": self.fio,
                "theme": self.selected_theme,
                "count": self.count,
                "date": __import__('datetime').datetime.now().isoformat(),
                "answers": self.answer_map
            }, f, ensure_ascii=False, indent=2)
        self.manager.get_screen("result").show_score(self.calc_score())
        self.manager.current = "result"

    def calc_score(self):
        correct = 0
        for i, q in enumerate(self.question_list):
            right = set(q.get("correct", []))
            ans = set(self.answer_map[i])
            if ans == right:
                correct += 1
        return int(100 * correct / self.count) if self.count else 0

class ResultScreen(Screen):
    def show_score(self, score):
        self.ids.score_label.text = f"Ваш результат: {score}%"

    def to_main(self):
        self.manager.current = "themes"

class AdminPinScreen(Screen):
    def check_pin(self):
        pin = self.ids.pin_input.text.strip()
        if pin == ADMIN_PIN:
            self.ids.error_label.text = ""
            self.manager.current = "admin"
        else:
            self.ids.error_label.text = "Невірний PIN"

    def go_back(self):
        self.manager.current = "themes"

class AdminScreen(Screen):
    def on_enter(self):
        pass

    def go_back(self):
        self.manager.current = "themes"

class KivyTestApp(App):
    def build(self):
        return Builder.load_file('app.kv')

if __name__ == "__main__":
    KivyTestApp().run()

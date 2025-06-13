# v0.4.8

import os
import json
from datetime import datetime
from kivy.uix.screenmanager import Screen

RESULTS_DIR = "results"
REPORTS_DIR = "reports"

class AdminScreen(Screen):
    pass
#    def on_enter(self):
#        self.ids.pin_input.text = ""
#        self.ids.pin_input.focus = True
#        self.ids.error_label.text = ""
#        self.ids.report_area.text = ""
#        self.pin_checked = False

    def check_pin(self):
        from main import config
        pin = self.ids.pin_input.text.strip()
        if pin == config["admin_pin"]:
            self.pin_checked = True
            self.ids.pin_box.opacity = 0
            self.ids.reports_box.opacity = 1
        else:
            self.ids.error_label.text = "Невірний PIN!"

    def back(self):
        self.manager.current = "theme"

    def generate_report(self, mode):
        # Собираем все результаты
        all_results = []
        for fname in os.listdir(RESULTS_DIR):
            if fname.endswith(".json"):
                with open(os.path.join(RESULTS_DIR, fname), encoding="utf-8") as f:
                    all_results.append(json.load(f))

        if mode == "by_theme":
            report = {}
            for r in all_results:
                report.setdefault(r["theme"], []).append(r["score"])
            lines = ["Результати по темах:"]
            for theme, scores in report.items():
                avg = sum(scores) / len(scores) if scores else 0
                lines.append(f"{theme}: {len(scores)} тестів, середній бал {avg:.2f}%")
            txt = "\n".join(lines)
        elif mode == "by_fio":
            report = {}
            for r in all_results:
                report.setdefault(r["fio"], []).append(r["score"])
            lines = ["Результати по ПІБ:"]
            for fio, scores in report.items():
                avg = sum(scores) / len(scores) if scores else 0
                lines.append(f"{fio}: {len(scores)} тестів, середній бал {avg:.2f}%")
            txt = "\n".join(lines)
        elif mode == "all":
            lines = ["Всі результати:"]
            for r in all_results:
                lines.append(f"{r['fio']} | {r['theme']} | {r['score']}% | {r['date']}")
            txt = "\n".join(lines)
        else:
            txt = "Необхідно обрати звіт!"
        self.ids.report_area.text = txt

        # Сохраняем отчёт
        rname = f"report_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(os.path.join(REPORTS_DIR, rname), "w", encoding="utf-8") as f:
            f.write(txt)

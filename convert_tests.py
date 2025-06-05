import os
import re
import json

def parse_questions(text):
    """
    Парсит текстовый файл с тестом и возвращает список вопросов в формате:
    [
        {
            "question": "<текст вопроса>",
            "options": ["Вариант A", "Вариант Б", ...],
            "correct": [индексы правильных вариантов]
        },
        ...
    ]
    """
    # Разбиение на блоки вопросов по пустой строке
    blocks = [b.strip() for b in text.strip().split('\n\n') if b.strip()]
    # Возможные метки вариантов
    letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е']
    letter_to_index = {l: i for i, l in enumerate(letters)}

    questions = []
    for block in blocks:
        lines = block.split('\n')
        # Убираем номер вопроса
        q_text = re.sub(r'^\d+\.\s*', '', lines[0]).strip()
        # Собираем варианты ответа
        opts = []
        for opt_line in lines[1:-1]:
            match = re.match(r'^([А-Е])\.\s*(.*)$', opt_line)
            if match:
                opts.append(match.group(2).strip())
        # Последняя строка: правильные ответы
        correct_part = lines[-1].split(':', 1)[1]
        answer_letters = [a.strip() for a in correct_part.split(',')]
        correct_indices = [letter_to_index[a] for a in answer_letters if a in letter_to_index]

        questions.append({
            "question": q_text,
            "options": opts,
            "correct": correct_indices
        })
    return questions

def convert_all(raw_dir='raw_tests', out_dir='questions'):
    """
    Конвертирует все .txt файлы из папки raw_dir в .json файлы в папке out_dir
    по формату, требуемому для приложения.
    """
    os.makedirs(out_dir, exist_ok=True)
    for fname in os.listdir(raw_dir):
        if not fname.lower().endswith('.txt'):
            continue
        path = os.path.join(raw_dir, fname)
        text = open(path, encoding='utf-8').read()
        qs = parse_questions(text)

        # Тема: имя файла без расширения
        theme = os.path.splitext(fname)[0]
        data = {
            "theme": theme,
            "num_questions": len(qs),
            "questions": qs
        }
        out_fname = theme + '.json'
        out_path = os.path.join(out_dir, out_fname)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'Converted {fname} → {out_fname}')

if __name__ == '__main__':
    convert_all()

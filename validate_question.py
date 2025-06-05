import os, json

def validate_qdir(qdir='questions'):
    bad = False
    for fname in os.listdir(qdir):
        if not fname.lower().endswith('.json'):
            continue
        path = os.path.join(qdir, fname)
        try:
            with open(path, encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            print(f'[ERROR] Файл {fname}: {e}')
            bad = True
    if not bad:
        print('Все JSON-файлы корректны!')

if __name__ == '__main__':
    validate_qdir()

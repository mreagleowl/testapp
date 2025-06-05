import os
import venv

env_dir = '.venv'

if os.path.exists(env_dir):
    print(f"Папка «{env_dir}» уже существует.")
else:
    # Создаём окружение с pip
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(env_dir)
    print(f"Виртуальное окружение создано в папке «{env_dir}».")

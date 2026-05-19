import os
import shutil
import time
import pathlib
import zipfile
import functions

os.makedirs("data", exist_ok=True)
todos_path = os.path.join("data", "todos.txt")

if not os.path.exists(todos_path):
    with open(todos_path, "w", encoding='utf-8') as f:
        pass

def add_todo(text: str):
    todo = text.strip()
    if not todo:
        raise ValueError
    todos = functions.get_todos()
    todos.append(todo + "\n")
    functions.write_todos(todos)

def show_todos():
    todos = functions.get_todos()
    for index, item in enumerate(todos):
        row = f"{index + 1} -- {item.strip()}"
        print(row)

def edit_todo(number: int, new_text: str):
    if number < 1:
        raise IndexError
    todos = functions.get_todos()
    todos[number - 1] = new_text.strip() + "\n"
    functions.write_todos(todos)

def complete_todo(number: int):
    if number < 1:
        raise IndexError
    todos = functions.get_todos()
    completed_todo = todos.pop(number - 1)
    functions.write_todos(todos)
    return completed_todo.strip()

def count_todos():
    todos = functions.get_todos()
    return len(todos)

def clear_todos():
    functions.write_todos([])

def backup_todos():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    backup_path = os.path.join("data", f"todos-backup-{timestamp}.txt")
    shutil.copy(todos_path, backup_path)
    return backup_path

def make_archive():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    dest_path = pathlib.Path('data', f'compressed-{timestamp}.zip')
    with zipfile.ZipFile(dest_path, 'w') as archive:
        archive.write(todos_path, arcname=pathlib.Path(todos_path).name)

# --- Додаткові функції як у викладача ---

def search_todos(query: str):
    todos = functions.get_todos()
    found = [t.strip() for t in todos if query.lower() in t.lower()]
    return found

def sort_todos():
    todos = functions.get_todos()
    todos.sort(key=str.lower)
    functions.write_todos(todos)

def filter_todos(keyword: str):
    todos = functions.get_todos()
    # Фільтрація повертає список, що не містить keyword
    filtered = [t for t in todos if keyword.lower() not in t.lower()]
    functions.write_todos(filtered)

if __name__ == '__main__':
    print(pathlib.Path(todos_path).name)
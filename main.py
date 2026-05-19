#!/usr/bin/env python3
import argparse
import time
import sys
import click
import typer

from core import (
    add_todo,
    show_todos,
    edit_todo,
    complete_todo,
    count_todos,
    clear_todos,
    backup_todos,
    search_todos,
    sort_todos,
    filter_todos
)

def success():
    print("Успішне виконання команди")

def do_add(user_action):
    add_todo(user_action[4:])
    return True

def do_show(user_action):
    show_todos()
    return True

def do_edit(user_action):
    number = int(user_action[5:])
    new_todo = input("Enter new todo: ")
    edit_todo(number, new_todo)
    return True

def do_complete(user_action):
    number = int(user_action[9:])
    completed_todo = complete_todo(number)
    print(f'\tТудушка "{completed_todo}" була успішно виконана!')
    return True

def do_count(user_action):
    total = count_todos()
    print(f"Кількість тудушок: {total}")
    return True

def do_clear(user_action):
    clear_todos()
    print("Список тудушок очищено.")
    return True

def do_backup(user_action):
    backup_file = backup_todos()
    print(f"Резервну копію створено: {backup_file}")
    return True

def do_search(user_action):
    query = user_action[7:].strip()
    results = search_todos(query)
    print(f"Знайдено: {results}")
    return True

def do_sort(user_action):
    sort_todos()
    print("Список відсортовано.")
    return True

def do_filter(user_action):
    keyword = user_action[7:].strip()
    filter_todos(keyword)
    print(f"Тудушки з словом '{keyword}' видалено.")
    return True

def do_exit(user_action):
    return False

# Таблиця команд (Command Dispatcher Table)
COMMANDS = {
    "add": do_add,
    "show": do_show,
    "edit": do_edit,
    "complete": do_complete,
    "count": do_count,
    "clear": do_clear,
    "backup": do_backup,
    "search": do_search,
    "sort": do_sort,
    "filter": do_filter,
    "exit": do_exit,
}

def dispatch(user_action):
    user_action = user_action.strip()
    if not user_action:
        print("invalid input")
        return True

    cmd = user_action.split(maxsplit=1)[0].lower()
    handler = COMMANDS.get(cmd)

    if handler is None:
        print("invalid input")
        return True

    try:
        should_continue = handler(user_action)
        if should_continue:
            success()
        return should_continue

    except ValueError:
        print("Ваша команда не зовсім зрозуміла")
        return True
    except IndexError:
        print("Не вірний номер тудушки")
        return True

def repl():
    now = time.strftime("%b %d, %Y %H:%M:%S")
    print(now)
    while True:
        user_action = input(
            "Type add, show, edit, complete, count, clear, backup, search, sort, filter or exit: "
        )
        if not dispatch(user_action):
            break
    print("Babay!")


# ---------------- argparse ----------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Todo: REPL (без аргументів) або CLI-команда (через argparse).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Додати тудушку")
    p_add.add_argument("text", nargs="+")

    sub.add_parser("show", help="Показати список")

    p_edit = sub.add_parser("edit", help="Редагувати тудушку")
    p_edit.add_argument("number", type=int)

    p_complete = sub.add_parser("complete", help="Завершити")
    p_complete.add_argument("number", type=int)

    sub.add_parser("count")
    sub.add_parser("clear")
    sub.add_parser("backup")
    sub.add_parser("sort")
    
    p_search = sub.add_parser("search")
    p_search.add_argument("query")

    p_filter = sub.add_parser("filter")
    p_filter.add_argument("keyword")

    sub.add_parser("repl")

    return parser

def run_from_args(args):
    try:
        if args.command == "add":
            add_todo(" ".join(args.text))
            success()
        elif args.command == "show":
            show_todos()
            success()
        elif args.command == "edit":
            new_todo = input("Enter new todo: ")
            edit_todo(args.number, new_todo)
            success()
        elif args.command == "complete":
            completed_todo = complete_todo(args.number)
            print(f'\tТудушка "{completed_todo}" була успішно виконана!')
            success()
        elif args.command == "count":
            print(f"Кількість: {count_todos()}")
            success()
        elif args.command == "clear":
            clear_todos(); success()
        elif args.command == "backup":
            backup_todos(); success()
        elif args.command == "sort":
            sort_todos(); success()
        elif args.command == "search":
            print(search_todos(args.query)); success()
        elif args.command == "filter":
            filter_todos(args.keyword); success()
        elif args.command == "repl":
            repl()
    except (ValueError, IndexError):
        print("Помилка виконання команди")

# ---------------- click ----------------

@click.group()
def click_cli():
    pass

@click_cli.command("add")
@click.argument("text", nargs=-1)
def click_add(text):
    add_todo(" ".join(text)); success()

@click_cli.command("show")
def click_show():
    show_todos(); success()

@click_cli.command("search")
@click.argument("query")
def click_search(query):
    print(search_todos(query)); success()

@click_cli.command("sort")
def click_sort():
    sort_todos(); success()

@click.group(help="Todo CLI через click (альтернатива argparse).")
def click_cli():
    pass

@click_cli.command("add")
@click.argument("text", nargs=-1)  # дозволяє писати без лапок: add Buy milk
def click_add(text):
    add_todo(" ".join(text))
    success()

@click_cli.command("show")
def click_show():
    show_todos()
    success()

@click_cli.command("edit")
@click.argument("number", type=int)
def click_edit(number):
    new_todo = input("Enter new todo: ")
    edit_todo(number, new_todo)
    success()

@click_cli.command("complete")
@click.argument("number", type=int)
def click_complete(number):
    completed_todo = complete_todo(number)
    print(f'\tТудушка "{completed_todo}" була успішно виконана!')
    success()

@click_cli.command("count")
def click_count():
    print(f"Кількість тудушок: {count_todos()}")
    success()


@click_cli.command("clear")
def click_clear():
    clear_todos()
    print("Список тудушок очищено.")
    success()


@click_cli.command("backup")
def click_backup():
    backup_file = backup_todos()
    print(f"Резервну копію створено: {backup_file}")
    success()

@click_cli.command("repl")
def click_repl():
    repl()

# ---------------- typer ----------------

typer_app = typer.Typer()

@typer_app.command()
def add(text: list[str]):
    add_todo(" ".join(text)); success()

@typer_app.command()
def search(query: str):
    print(search_todos(query)); success()

@typer_app.command()
def sort():
    sort_todos(); success()

@typer_app.command()
def add(text: list[str]):
    add_todo(" ".join(text))
    success()


@typer_app.command()
def show():
    show_todos()
    success()


@typer_app.command()
def edit(number: int):
    try:
        new_todo = input("Enter new todo: ")
        edit_todo(number, new_todo)
        success()
    except IndexError:
        print("Не вірний номер тудушки")
        raise typer.Exit()


@typer_app.command()
def complete(number: int):
    try:
        completed_todo = complete_todo(number)
        print(f'\tТудушка "{completed_todo}" була успішно виконана!')
        success()
    except IndexError:
        print("Не вірний номер тудушки")
        raise typer.Exit()

@typer_app.command()
def count():
    print(f"Кількість тудушок: {count_todos()}")
    success()


@typer_app.command()
def clear():
    clear_todos()
    print("Список тудушок очищено.")
    success()


@typer_app.command()
def backup():
    backup_file = backup_todos()
    print(f"Резервну копію створено: {backup_file}")
    success()

@typer_app.command()
def repl_command():
    repl()

def main():
    if len(sys.argv) == 1:
        repl()
        return

    if sys.argv[1] == "click":
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        click_cli()
        return

    if sys.argv[1] == "typer":
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        typer_app()
        return

    parser = build_parser()
    args = parser.parse_args()
    run_from_args(args)

if __name__ == '__main__':
    main()
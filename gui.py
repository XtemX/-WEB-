import FreeSimpleGUI as sg
import functions
import core
import time
from datetime import datetime

# =========================
# СВІТЛО-БЛАКИТНА ТЕМА
# =========================
cyan_theme = {
    'BACKGROUND': '#0D1117',
    'TEXT': '#E6EDF3',
    'INPUT': '#161B22',
    'TEXT_INPUT': '#98E4FF',
    'SCROLL': '#21262D',
    'BUTTON': ('#0B0F14', '#98E4FF'),
    'PROGRESS': ('#98E4FF', '#0D1117'),
    'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
}
sg.theme_add_new('LightBlueTodo', cyan_theme)
sg.theme('LightBlueTodo')

def get_ukr_date():
    months = {1: "січня", 2: "лютого", 3: "березня", 4: "квітня", 5: "травня", 6: "червня",
              7: "липня", 8: "серпня", 9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"}
    now = datetime.now()
    return f"{now.day} {months[now.month]} {now.year}"

def get_table_data():
    """Отримує актуальні дані з файлу"""
    todos = functions.get_todos()
    data = []
    for item in todos:
        if not item.strip() or '|' not in item: continue
        p = [x.strip() for x in item.split('|')]
        task, date, status = p[0], p[1], p[2]
        
        icon = "✅" if "Виконано" in status else "⏳"
        if icon == "⏳":
            try:
                if datetime.strptime(date, "%d.%m.%Y").date() < datetime.now().date():
                    icon = "🔴"
            except: pass
        data.append([icon, task, date, status])
    return data

btn = lambda t, k, c='#98E4FF': sg.Button(t, key=k, size=(16, 1), font=('Segoe UI', 10, 'bold'), button_color=('#0B0F14', c), border_width=0)

# --- LAYOUT ---
sidebar = sg.Column([
    [sg.Text('МЕНЮ', font=('Segoe UI', 14, 'bold'), text_color='#98E4FF')],
    [btn('➕ Додати', 'add', '#98E4FF')],
    [btn('✏️ Редагувати', 'edit', '#00B4D8')],
    [btn('✔ Виконано', 'complete', '#48CAE4')],
    [sg.HSep(pad=(0,10), color='#1B222C')],
    [btn('🔍 Пошук', 'search', '#607D8B')],
    [btn('🔃 Сортування', 'sort', '#607D8B')],
    [btn('📊 Статистика', 'count', '#607D8B')], # КНОПКА СТАТИСТИКИ
    [sg.HSep(pad=(0,10), color='#1B222C')],
    [btn('💾 Бекап', 'backup', '#607D8B')],
    [btn('📦 Архів', 'compress', '#607D8B')],
    [btn('🔄 Скинути', 'reset', '#607D8B')],
    [sg.VPush()],
    [btn('🗑 Очистити', 'clear', '#CF6679')],
    [btn('🚪 Вихід', 'exit', '#546E7A')],
], vertical_alignment='top', pad=(10, 10))

content = sg.Column([
    [sg.Text('Мій Список Справ', font=('Segoe UI', 24, 'bold'), text_color="#98E4FF")],
    [sg.Frame('', [[
        sg.Text('📅 ' + get_ukr_date()), sg.VerticalSeparator(),
        sg.Text('', key='clock', font=('Consolas', 14, 'bold'), text_color='#98E4FF')
    ]], border_width=0, background_color='#161B22', pad=(0, 10))],

    [sg.Frame('Швидкий ввід', [
        [sg.Input(key='task_in', size=(40, 1)), 
         sg.Input(time.strftime('%d.%m.%Y'), key='date_in', size=(12, 1)),
         sg.CalendarButton('📅', target='date_in', format='%d.%m.%Y')]
    ], title_color='#98E4FF')],

    [sg.Table(values=get_table_data(), 
              headings=[' ', 'Задача', 'Термін', 'Статус'], 
              key='main_table',
              col_widths=[3, 40, 12, 12],
              auto_size_columns=False,
              num_rows=15,
              enable_events=True,
              background_color='#161B22',
              header_background_color='#1B222C',
              selected_row_colors=('#0B0F14', '#98E4FF'))]
], pad=(10, 10))

layout = [[sidebar, sg.VSeparator(color='#1B222C'), content]]
window = sg.Window('Todo App Final', layout, finalize=True)

# --- MAIN LOOP ---
while True:
    event, values = window.read(timeout=1000)
    window['clock'].update(time.strftime('%H:%M:%S'))

    if event in (sg.WIN_CLOSED, 'exit'):
        break

    if event == 'main_table' and values['main_table']:
        idx = values['main_table'][0]
        row = get_table_data()[idx]
        window['task_in'].update(row[1])
        window['date_in'].update(row[2])

    # --- ЛОГІКА КНОПОК ---
    if event == 'add':
        if values['task_in'].strip():
            core.add_todo(f"{values['task_in']} | {values['date_in']} | В процесі")
            window['main_table'].update(values=get_table_data())
            window['task_in'].update('')

    elif event == 'complete':
        if values['main_table']:
            idx = values['main_table'][0]
            rows = get_table_data()
            t_name, t_date = rows[idx][1], rows[idx][2]
            todos = functions.get_todos()
            for i, line in enumerate(todos):
                if t_name in line and t_date in line:
                    todos[i] = f"{t_name} | {t_date} | Виконано\n"
                    break
            functions.write_todos(todos)
            window['main_table'].update(values=get_table_data())

    elif event == 'count':
        # РОЗШИРЕНА СТАТИСТИКА
        data = get_table_data()
        total = len(data)
        done = sum(1 for r in data if r[0] == "✅")
        active = total - done
        sg.popup(f"📊 СТАТИСТИКА ЗАВДАНЬ:\n\n"
                 f"🔹 Всього: {total}\n"
                 f"✅ Виконано: {done}\n"
                 f"⏳ В процесі: {active}", 
                 title="Інфо", background_color='#1B222C', custom_text="Зрозуміло")

    elif event == 'edit':
        if values['main_table']:
            idx = values['main_table'][0]
            old_task = get_table_data()[idx][1]
            todos = functions.get_todos()
            for i, line in enumerate(todos):
                if old_task in line:
                    todos[i] = f"{values['task_in']} | {values['date_in']} | В процесі\n"
                    break
            functions.write_todos(todos)
            window['main_table'].update(values=get_table_data())

    elif event == 'sort':
        core.sort_todos()
        window['main_table'].update(values=get_table_data())

    elif event == 'search':
        if values['task_in']:
            results = core.search_todos(values['task_in'])
            window['main_table'].update(values=[["🔍", r.split('|')[0], r.split('|')[1], r.split('|')[2]] for r in results if '|' in r])

    elif event == 'reset':
        window['main_table'].update(values=get_table_data())

    elif event == 'clear':
        if sg.popup_yes_no("Очистити все?") == 'Yes':
            core.clear_todos()
            window['main_table'].update(values=get_table_data())

window.close()
import streamlit as st
import functions
import core
import time
from datetime import datetime

# =========================
# СТИЛІЗАЦІЯ (CYAN THEME)
# =========================
st.set_page_config(page_title="Todo System Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0D1117; color: #E6EDF3; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #21262D; min-width: 250px; }
    
    /* Кнопки в бічній панелі */
    .stButton>button {
        background-color: #1B222C; color: #98E4FF;
        border: 1px solid #98E4FF; font-weight: bold;
        width: 100%; border-radius: 4px; margin-bottom: -10px;
    }
    .stButton>button:hover { background-color: #98E4FF; color: #0D1117; }
    
    /* Спеціальна червона кнопка для Очистити */
    div[data-testid="stSidebar"] .stButton:nth-last-child(2) button {
        border-color: #CF6679; color: #CF6679;
    }
    
    /* Поля вводу */
    input { background-color: #0D1117 !important; color: #98E4FF !important; }
    </style>
    """, unsafe_allow_html=True)

def get_ukr_date():
    months = {1: "січня", 2: "лютого", 3: "березня", 4: "квітня", 5: "травня", 6: "червня",
              7: "липня", 8: "серпня", 9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"}
    now = datetime.now()
    return f"{now.day} {months[now.month]} {now.year}"

def get_table_data():
    todos = functions.get_todos()
    data = []
    for item in todos:
        if not item.strip() or '|' not in item: continue
        p = [x.strip() for x in item.split('|')]
        icon = "✅" if "Виконано" in p[2] else "⏳"
        if icon == "⏳":
            try:
                if datetime.strptime(p[1], "%d.%m.%Y").date() < datetime.now().date():
                    icon = "🔴"
            except: pass
        data.append({"Статус": icon, "Задача": p[0], "Термін": p[1], "Стан": p[2]})
    return data

# --- SIDEBAR: ВСІ КНОПКИ ТУТ ---
with st.sidebar:
    st.markdown("<h2 style='color: #98E4FF; text-align: center;'>МЕНЮ</h2>", unsafe_allow_html=True)
    
    # Група: Основні
    if st.button("➕ Додати"):
        if st.session_state.get('task_input'):
            core.add_todo(f"{st.session_state.task_input} | {st.session_state.date_input.strftime('%d.%m.%Y')} | В процесі")
            st.rerun()

    # Створюємо селектбокс для кнопок, які потребують вибору задачі
    all_data = get_table_data()
    task_names = [d["Задача"] for d in all_data]
    selected = st.selectbox("Вибір задачі для дій:", task_names if task_names else ["Список порожній"])

    if st.button("✏️ Редагувати"):
        if selected != "Список порожній" and st.session_state.get('task_input'):
            todos = functions.get_todos()
            for i, line in enumerate(todos):
                if selected in line:
                    todos[i] = f"{st.session_state.task_input} | {st.session_state.date_input.strftime('%d.%m.%Y')} | В процесі\n"
                    break
            functions.write_todos(todos)
            st.rerun()

    if st.button("✔ Виконано"):
        if selected != "Список порожній":
            todos = functions.get_todos()
            for i, line in enumerate(todos):
                if selected in line:
                    p = line.split('|')
                    todos[i] = f"{p[0].strip()} | {p[1].strip()} | Виконано\n"
                    break
            functions.write_todos(todos)
            st.rerun()

    st.markdown("---")
    
    # Група: Функції
    if st.button("🔍 Пошук"):
        if st.session_state.get('task_input'):
            st.session_state.search_mode = True
        else: st.sidebar.warning("Введіть текст для пошуку")

    if st.button("🔃 Сортування"):
        core.sort_todos()
        st.rerun()

    if st.button("📊 Статистика"):
        total = len(all_data)
        done = sum(1 for r in all_data if r["Статус"] == "✅")
        st.sidebar.info(f"Всього: {total} | ✅: {done} | ⏳: {total-done}")

    st.markdown("---")
    
    # Група: Системні
    if st.button("💾 Бекап"):
        core.backup_todos()
        st.sidebar.success("Збережено!")

    if st.button("📦 Архів"):
        core.make_archive()
        st.sidebar.success("Архів створено!")

    if st.button("🔄 Скинути"):
        st.session_state.search_mode = False
        st.rerun()

    st.spacer = st.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.button("🗑 Очистити"):
        core.clear_todos()
        st.rerun()

    if st.button("🚪 Вихід"):
        st.stop()

# --- ГОЛОВНИЙ ЕКРАН ---
st.markdown("<h1 style='text-align: center; color: #98E4FF;'>Мій Список Справ</h1>", unsafe_allow_html=True)

# Годинник
@st.fragment(run_every=1)
def clock():
    st.markdown(f"<div style='text-align: center; background: #161B22; padding: 5px; border-radius: 8px; border: 1px solid #21262D;'>"
                f"📅 {get_ukr_date()} | <b style='color: #98E4FF;'>🕒 {datetime.now().strftime('%H:%M:%S')}</b></div>", unsafe_allow_html=True)
clock()

# Ввід даних
with st.container(border=True):
    c1, c2 = st.columns([3, 1])
    task_txt = c1.text_input("Назва задачі", key="task_input", placeholder="Наприклад: Вивчити Streamlit")
    task_dt = c2.date_input("Термін", key="date_input")

# Таблиця
current_data = get_table_data()

# Логіка пошуку
if st.session_state.get('search_mode') and st.session_state.task_input:
    query = st.session_state.task_input.lower()
    current_data = [d for d in current_data if query in d["Задача"].lower()]
    st.caption(f"Результати пошуку для: {query}")

if current_data:
    st.dataframe(current_data, use_container_width=True, hide_index=True)
else:
    st.write("Задач не знайдено 🕸")
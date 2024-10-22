import os
import streamlit as st
import sqlite3
import time

# SQLiteデータベースの初期化
DB_PATH = "/app/data/tasks.db"

# SQLiteデータベースの初期化
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                estimated_time INTEGER NOT NULL,
                elapsed_time INTEGER NOT NULL DEFAULT 0,
                is_running BOOLEAN NOT NULL DEFAULT 0,
                start_time REAL
            )
        ''')
        conn.commit()
        conn.close()

# タスクの追加
def add_task(name, estimated_time):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO tasks (name, estimated_time) VALUES (?, ?)', (name, estimated_time))
    conn.commit()
    conn.close()

# タスクの読み込み
def load_tasks():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    conn.close()
    return tasks

# タスクの更新
def update_task(task_id, elapsed_time=None, is_running=None, start_time=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if elapsed_time is not None:
        c.execute('UPDATE tasks SET elapsed_time = ? WHERE id = ?', (elapsed_time, task_id))
    if is_running is not None:
        c.execute('UPDATE tasks SET is_running = ? WHERE id = ?', (is_running, task_id))
    if start_time is not None:
        c.execute('UPDATE tasks SET start_time = ? WHERE id = ?', (start_time, task_id))
    conn.commit()
    conn.close()

# タスクの削除
def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

# タイマーを更新するための関数
def update_timer():
    tasks = load_tasks()
    for task in tasks:
        task_id, name, estimated_time, elapsed_time, is_running, start_time = task
        if is_running:
            current_time = time.time()
            new_elapsed_time = elapsed_time + int(current_time - start_time)
            update_task(task_id, elapsed_time=new_elapsed_time, start_time=current_time)

# アプリケーションの初期化
init_db()
st.title("TODO Management System")

# タスクの追加
with st.form("add_task_form"):
    task_name = st.text_input("Task Name")
    estimated_time = st.number_input("Estimated Time (minutes)", min_value=1, step=1)
    add_task_button = st.form_submit_button("Add Task")
    if add_task_button:
        add_task(task_name, estimated_time)
        st.success(f"Task '{task_name}' added successfully!")

# タスクの表示
tasks = load_tasks()
for task in tasks:
    task_id, name, estimated_time, elapsed_time, is_running, start_time = task
    with st.container():
        st.write(f"### {name}")
        st.write(f"Estimated Time: {estimated_time} minutes")
        st.write(f"Elapsed Time: {(elapsed_time // 60):02d}:{(elapsed_time % 60):02d}{' (Running😎)' if is_running else ''}")

        # タイマーの制御
        if is_running:
            elapsed_time = elapsed_time + int(time.time() - start_time)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Stop", key=f"stop_{task_id}"):
                    update_task(task_id, is_running=0, elapsed_time=elapsed_time)
                    st.rerun()
            with col2:
                if st.button(f"Reset", key=f"reset_{task_id}"):
                    update_task(task_id, elapsed_time=0, is_running=0)
                    st.rerun()
        else:
            if st.button(f"Start", key=f"start_{task_id}"):
                update_task(task_id, is_running=1, start_time=time.time())
                st.rerun()

        # タスクの削除
        if st.button(f"Delete", key=f"delete_{task_id}"):
            delete_task(task_id)
            st.success(f"Task '{name}' deleted successfully!")
            st.rerun()

# タイマーの定期更新
if any(task[4] for task in tasks):  # いずれかのタスクが実行中かどうか
    update_timer()
    time.sleep(1)
    st.rerun()

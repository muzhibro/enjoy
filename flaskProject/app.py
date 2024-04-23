from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# MySQL数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '112385',
    'database': 'login'
}
# 创建数据库连接
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()
# 创建用户表格（如果不存在）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    )
''')
# 创建团队成员表格（如果不存在）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_members (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    )
''')
# 创建任务表格（如果不存在）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        deadline DATE,
        assigned_to VARCHAR(255),
        priority char(10),
        status char(20)
    )
''')
# 提交更改并关闭连接
conn.commit()
cursor.close()
conn.close()

tasks = []

# Placeholder for logged-in user
logged_in_user = None


class TeamMember:
    def __init__(self, name):
        self.name = name


team_members = []


class Task:
    def __init__(self, title, description, deadline, assigned_to, priority,status):
        self.id = None
        self.title = title
        self.description = description
        self.deadline = deadline
        self.assigned_to = assigned_to
        self.priority = priority
        self.status = status



@app.route('/')
def login_redirect():
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in_user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 查询用户是否存在于数据库中
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            logged_in_user = username
            # flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    global logged_in_user
    logged_in_user = None
    # flash('Logged out successfully', 'info')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 检查用户名是否已存在
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('register'))
        else:
            # 将新用户添加到数据库中
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Registration successful', 'success')
            return render_template('register.html', show_dialog=True)
    return render_template('register.html', show_dialog=False)


@app.route('/home')
def home():
    # 加载团队成员和任务
    load_team_members_from_db()
    load_tasks_from_db()

    if logged_in_user:
        return render_template('index.html', tasks=tasks, team_members=team_members)
    else:
        return redirect(url_for('login'))


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d') if request.form['deadline'] else None
        assigned_to = request.form['assigned_to']
        priority = request.form['priority']
        status = "进行中"
        # 将新任务添加到数据库中
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tasks (title, description, deadline, assigned_to, priority, status) VALUES (%s, %s, %s, %s, %s, %s)',
            (title, description, deadline, assigned_to, priority, status))
        conn.commit()
        cursor.close()
        conn.close()

        new_task = Task(title=title, description=description, deadline=deadline, assigned_to=assigned_to,
                        priority=priority,status=status)
        tasks.append(new_task)

        # flash('Task created successfully', 'success')
        return redirect(url_for('home'))

    return render_template('create.html', team_members=team_members)


# @app.route('/complete/<int:id>')
# def complete(id):
#     for task in tasks:
#         if task.id == id:
#             task.completed = True
#
#             # 更新数据库中任务的完成状态
#             conn = mysql.connector.connect(**db_config)
#             cursor = conn.cursor()
#             cursor.execute('UPDATE tasks SET completed = TRUE WHERE id = %s', (id,))
#             conn.commit()
#             cursor.close()
#             conn.close()
#
#             flash('Task completed successfully', 'success')
#             break
#     return redirect(url_for('home'))



@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form['name']
    if name:
        # 检查是否已存在同名成员
        if any(member.name == name for member in team_members):
            flash('组员已存在', 'error')
        else:
            # 将新成员添加到数据库中
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO team_members (name) VALUES (%s)', (name,))
                conn.commit()
                cursor.close()
                conn.close()

                new_member = TeamMember(name)
                team_members.append(new_member)
                flash('添加成功', 'success')
            except mysql.connector.Error as e:
                flash('添加组员失败，请稍后尝试', 'error')
    else:
        flash('Name cannot be empty', 'error')
    return redirect(url_for('home'))



@app.route('/all_tasks')
def all_tasks():
    return render_template('all_tasks.html', tasks=tasks)




@app.route('/delete_task/<int:id>', methods=['POST'])
def delete_task(id):
    global tasks
    if request.method == 'POST':
        tasks = [task for task in tasks if task.id != id]

        # 从数据库中删除任务
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Task deleted successfully', 'success')
        return redirect(url_for('all_tasks'))
    else:
        return redirect(url_for('all_tasks'))


@app.route('/delete_member/<string:name>', methods=['POST'])
def delete_member(name):
    global team_members
    team_members = [member for member in team_members if member.name != name]

    # 从数据库中删除成员
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM team_members WHERE name = %s', (name,))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f'Team member {name} deleted successfully', 'success')
    return redirect(url_for('home'))


@app.route('/update_task_status/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    if request.method == 'POST' and 'status' in request.json:
        status = request.json['status']
        for task in tasks:
            if task.id == task_id:
                task.status = status

                # 更新数据库中任务的状态
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                cursor.execute('UPDATE tasks SET status = %s WHERE id = %s', (status, task_id))
                conn.commit()
                cursor.close()
                conn.close()

                flash(f'Task status updated to {status} successfully', 'success')
                break
    return redirect(url_for('home'))


# 在应用启动时加载团队成员
def load_team_members_from_db():
    global team_members
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM team_members')
    rows = cursor.fetchall()
    team_members = [TeamMember(row[0]) for row in rows]
    cursor.close()
    conn.close()


def load_tasks_from_db():
    global tasks
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tasks')
    rows = cursor.fetchall()
    tasks = []
    for row in rows:
        task = Task(title=row['title'], description=row['description'], deadline=row['deadline'],
                    assigned_to=row['assigned_to'], priority=row['priority'], status=row['status'])
        task.id = row['id']
        tasks.append(task)
    cursor.close()
    conn.close()

@app.route('/search_tasks', methods=['POST'])
def search_tasks():
    search_text = request.form['search_text']
    if search_text:
        # 从数据库中搜索匹配的任务
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE title LIKE %s OR description LIKE %s OR assigned_to LIKE %s OR status LIKE %s
        ''', ('%' + search_text + '%', '%' + search_text + '%', '%' + search_text + '%', '%' + search_text + '%'))
        rows = cursor.fetchall()
        tasks = [Task(**row) for row in rows]
        cursor.close()
        conn.close()
        return render_template('all_tasks.html', tasks=tasks)
    else:
        # 如果搜索文本为空，则重定向回显示所有任务的页面
        return redirect(url_for('all_tasks'))



if __name__ == '__main__':
    app.run(debug=True)

import sqlite3

# 连接到数据库
conn = sqlite3.connect('student_database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 查询students表
print("===== 学生表 =====")
cursor.execute('SELECT * FROM students')
students = cursor.fetchall()
for student in students:
    print(dict(student))

# 查询grades表
print("\n===== 成绩表 =====")
cursor.execute('SELECT * FROM grades')
grades = cursor.fetchall()
for grade in grades:
    print(dict(grade))

# 查询subjects表
print("\n===== 科目表 =====")
cursor.execute('SELECT * FROM subjects')
subjects = cursor.fetchall()
for subject in subjects:
    print(dict(subject))

conn.close()
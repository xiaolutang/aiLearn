import sqlite3
import pandas as pd
from faker import Faker
import random

# 初始化Faker实例，用于生成中文数据
fake = Faker('zh_CN')

# 数据库和Excel文件路径
DB_PATH = '/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/student_database.db'
EXCEL_PATH = '/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/student_data.xlsx'

# 科目列表
SUBJECTS = ['语文', '数学', '英语', '政治', '历史', '地理', '生物', '化学', '物理']
# 班级列表
CLASSES = ['1班', '2班', '3班', '4班', '5班', '6班']
# 考试类型
EXAM_TYPES = ['月考1', '月考2', '月考3', '期末考试']

# 生成唯一邮箱后缀，避免邮箱重复
email_suffix = 0

# 连接数据库
def connect_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

# 初始化数据库表
def init_db(conn):
    with open('/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/student_database_schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()

# 插入科目数据
def insert_subjects(conn):
    cursor = conn.cursor()
    for subject in SUBJECTS:
        try:
            cursor.execute('''
                INSERT INTO subjects (subject_name, credit) VALUES (?, 3)
            ''', (subject,))
        except sqlite3.IntegrityError:
            pass
    conn.commit()

# 插入班级数据
def insert_classes(conn):
    cursor = conn.cursor()
    for class_name in CLASSES:
        try:
            cursor.execute('''
                INSERT INTO classes (class_name, grade, academic_year) VALUES (?, 1, '2025')
            ''', (class_name,))
        except sqlite3.IntegrityError:
            pass
    conn.commit()

# 获取班级ID
def get_class_ids(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT class_id FROM classes')
    return [row[0] for row in cursor.fetchall()]

# 插入学生数据
def insert_students(conn):
    global email_suffix
    class_ids = get_class_ids(conn)
    cursor = conn.cursor()
    for class_id in class_ids:
        for _ in range(50):
            gender = random.choice(['男', '女'])
            name = fake.name_male() if gender == '男' else fake.name_female()
            birth_date = fake.date_of_birth(minimum_age=15, maximum_age=18)
            contact_number = fake.phone_number()
            email = f'{name}{email_suffix}@{fake.free_email_domain()}'
            email_suffix += 1
            address = fake.address().replace('\n', '')
            
            try:
                cursor.execute('''
                    INSERT INTO students (student_name, gender, birth_date, class_id, contact_number, email, address) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, gender, birth_date, class_id, contact_number, email, address))
            except sqlite3.IntegrityError:
                continue
    conn.commit()

# 获取学生ID和科目ID
def get_student_and_subject_ids(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT student_id FROM students')
    student_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT subject_id FROM subjects')
    subject_ids = [row[0] for row in cursor.fetchall()]
    return student_ids, subject_ids

# 插入成绩数据
def insert_grades(conn):
    student_ids, subject_ids = get_student_and_subject_ids(conn)
    cursor = conn.cursor()
    
    for exam_type in EXAM_TYPES:
        exam_date = fake.date_between(start_date='-1y', end_date='today')
        for student_id in student_ids:
            for subject_id in subject_ids:
                score = round(random.uniform(0, 100), 2)
                try:
                    cursor.execute('''
                        INSERT INTO grades (student_id, subject_id, exam_date, score, exam_type) VALUES (?, ?, ?, ?, ?)
                    ''', (student_id, subject_id, exam_date, score, exam_type))
                except sqlite3.IntegrityError:
                    continue
    conn.commit()

# 将数据导出到Excel
def export_to_excel(conn):
    tables = ['students', 'classes', 'subjects', 'grades']
    with pd.ExcelWriter(EXCEL_PATH) as writer:
        for table in tables:
            df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
            df.to_excel(writer, sheet_name=table, index=False)

# 检查数据是否符合要求
def check_data(conn):
    cursor = conn.cursor()
    
    # 检查科目数量
    cursor.execute('SELECT COUNT(*) FROM subjects')
    if cursor.fetchone()[0] != len(SUBJECTS):
        return False
    
    # 检查班级数量
    cursor.execute('SELECT COUNT(*) FROM classes')
    if cursor.fetchone()[0] != len(CLASSES):
        return False
    
    # 检查学生数量
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] != 300:
        return False
    
    return True

# 删除所有数据
def delete_all_data(conn):
    tables = ['students', 'classes', 'subjects', 'grades']
    cursor = conn.cursor()
    for table in tables:
        cursor.execute(f'DELETE FROM {table}')
    conn.commit()

# 主函数
def main():
    conn = connect_db()
    init_db(conn)
    
    while True:
        delete_all_data(conn)
        insert_subjects(conn)
        insert_classes(conn)
        insert_students(conn)
        insert_grades(conn)
        
        if check_data(conn):
            export_to_excel(conn)
            break
        
    conn.close()
    print('模拟数据录入成功！')

if __name__ == '__main__':
    main()
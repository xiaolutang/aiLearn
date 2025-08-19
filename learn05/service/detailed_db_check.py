import sqlite3

# 连接到数据库
conn = sqlite3.connect('student_database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("===== 数据库关系检查 =====")

# 1. 检查数学科目的subject_id
print("\n1. 数学科目的ID:")
cursor.execute("SELECT subject_id, subject_name FROM subjects WHERE subject_name = '数学'")
math_subjects = cursor.fetchall()
if math_subjects:
    for subject in math_subjects:
        print(f"数学科目ID: {subject['subject_id']}, 科目名称: {subject['subject_name']}")
else:
    print("未找到数学科目!")

# 2. 检查有多少成绩记录关联到数学科目
math_subject_id = math_subjects[0]['subject_id'] if math_subjects else None
if math_subject_id:
    print(f"\n2. 关联到数学科目(ID: {math_subject_id})的成绩记录数:")
    cursor.execute("SELECT COUNT(*) as count FROM grades WHERE subject_id = ?", (math_subject_id,))
    count = cursor.fetchone()['count']
    print(f"共有 {count} 条数学成绩记录")

    # 3. 检查这些成绩记录是否关联到有效的学生
    print("\n3. 数学成绩记录关联的学生情况:")
    cursor.execute("""
        SELECT g.grade_id, g.student_id, s.student_name
        FROM grades g
        LEFT JOIN students s ON g.student_id = s.student_id
        WHERE g.subject_id = ?
        LIMIT 10
    """, (math_subject_id,))
    results = cursor.fetchall()
    if results:
        print("成绩ID | 学生ID | 学生姓名")
        print("-------|--------|--------")
        for row in results:
            student_name = row['student_name'] if row['student_name'] else "未找到对应学生"
            print(f"{row['grade_id']} | {row['student_id']} | {student_name}")
        print(f"... 仅显示前10条记录")
    else:
        print("没有找到关联到数学科目的成绩记录")

    # 4. 执行与我们应用相同的查询
    print("\n4. 执行应用中的查询:")
    cursor.execute("""
        SELECT s.student_name, g.score 
        FROM grades g 
        JOIN students s ON g.student_id = s.student_id 
        JOIN subjects sub ON g.subject_id = sub.subject_id 
        WHERE sub.subject_name = '数学' 
        ORDER BY g.score DESC
    """)
    query_results = cursor.fetchall()
    if query_results:
        print("学生姓名 | 成绩")
        print("--------|------")
        for row in query_results:
            print(f"{row['student_name']} | {row['score']}")
    else:
        print("查询结果为空，可能是因为没有学生同时在students表和grades表中有记录")

# 5. 检查学生表和成绩表的学生ID匹配情况
print("\n5. 学生表和成绩表的学生ID匹配情况:")
cursor.execute("""
    SELECT COUNT(DISTINCT s.student_id) as student_count,
           COUNT(DISTINCT g.student_id) as grade_student_count,
           COUNT(DISTINCT g.student_id) FILTER (WHERE s.student_id IS NOT NULL) as matched_count
    FROM students s
    FULL OUTER JOIN grades g ON s.student_id = g.student_id
""")
stats = cursor.fetchone()
print(f"学生表中的学生数: {stats['student_count']}")
print(f"成绩表中关联的学生数: {stats['grade_student_count']}")
print(f"两表中匹配的学生数: {stats['matched_count']}")

conn.close()
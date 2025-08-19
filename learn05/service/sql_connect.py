from langchain_community.utilities import SQLDatabase

# 存储已打印的内容类型

class DatabaseManager:
    def __init__(self, db_uri="sqlite:///student_database.db"):
        """初始化数据库连接"""
        self.db = SQLDatabase.from_uri(db_uri)

    def get_table_info(self, table_names):
        """获取指定表的结构信息"""
        return self.db.get_table_info(table_names)

    def run_query(self, query):
        """执行SQL查询"""
        return self.db.run(query)

    def add_record(self, table_name, data):
        """
        向指定表添加记录
        :param table_name: 表名
        :param data: 字典，键为列名，值为对应的值
        """
        columns = ', '.join(data.keys())
        values = []
        for v in data.values():
            if isinstance(v, (int, float)):
                values.append(str(v))
            else:
                values.append(f"'{str(v).replace("'", "''")}'")
        values_str = ', '.join(values)
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values_str})"
        print(f'执行的 SQL 语句: {query}')
        self.db.run(query)

    def delete_record(self, table_name, condition):
        """
        从指定表删除记录
        :param table_name: 表名
        :param condition: 删除条件，例如 "student_id = 1"
        """
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.db.run(query)

    def update_record(self, table_name, data, condition):
        """
        更新指定表的记录
        :param table_name: 表名
        :param data: 字典，键为列名，值为对应的值
        :param condition: 更新条件，例如 "student_id = 1"
        """
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        self.db.run(query, tuple(data.values()))

    def get_records(self, table_name, columns="*", condition="", limit=None):
        """
        查询指定表的记录
        :param table_name: 表名
        :param columns: 要查询的列，默认为所有列
        :param condition: 查询条件，默认为空
        :param limit: 返回记录数量限制，默认为无限制
        """
        query = f"SELECT {columns} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        if limit:
            query += f" LIMIT {limit}"
        return self.db.run(query)

    def create_table(self, table_name, columns):
        """
        创建新表
        :param table_name: 表名
        :param columns: 列定义，例如 "id INTEGER PRIMARY KEY, name TEXT NOT NULL"
        """
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.db.run(query)

    def alter_table(self, table_name, operation):
        """
        更新表结构
        :param table_name: 表名
        :param operation: 表结构变更操作，例如 "ADD COLUMN age INTEGER"
        """
        query = f"ALTER TABLE {table_name} {operation}"
        self.db.run(query)

if __name__ == "__main__":
    # 示例用法
    db_manager = DatabaseManager()
    
    # 执行 schema 文件创建表
    try:
        with open('/Users/tangxiaolu/project/PythonProject/aiLearn/learn05/student_database_schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        # 移除注释行后再分割 SQL 语句
        sql_script = ''.join([line for line in sql_script.splitlines() if not line.strip().startswith('--')])
        queries = [q.strip() for q in sql_script.strip().split(';') if q.strip()]
        for query in queries:
            cleaned_query = query.strip()
            print(f" SQL 语句:\n\n  {cleaned_query}")
            print("  ====== "*30)
            if cleaned_query:
                # 优化执行日志，显示更多信息
                print(f"准备执行 SQL 查询，前 50 字符: {cleaned_query[:50]}...")
                try:
                    result = db_manager.run_query(cleaned_query)
                    print("查询执行成功！")
                except Exception as e:
                    print(f"查询执行失败，SQL 语句: {cleaned_query}\n错误信息: {str(e)}")

    except Exception as e:
        print(f"Error executing schema script: {e}")
    
    # 查看学生表结构信息
    print("学生表信息:")
    table_info = db_manager.get_table_info(["students"])
    print(table_info)

    # 查询前3条学生记录
    print("\n前3条学生记录:")
    students = db_manager.get_records("students", "student_id, student_name, gender", limit=3)
    print(students)

    # 查询班级信息
    print("\n班级信息:")
    classes = db_manager.get_records("classes", "class_id, class_name, grade")
    print(classes)

    # 查询教师信息
    print("\n教师信息:")
    teachers = db_manager.get_records("teachers", "teacher_id, teacher_name")
    print(teachers)

    # 示例：创建新表
    db_manager.create_table("new_table", "id INTEGER PRIMARY KEY, name TEXT NOT NULL")
    print("\n新表创建成功")

    # 示例：更新表结构
    try:
        table_info = db_manager.get_table_info(["new_table"])
        if "age" not in table_info:
            db_manager.alter_table("new_table", "ADD COLUMN age INTEGER")
            print("表结构更新成功")
        else:
            print("age 列已存在，无需重复添加")
    except Exception as e:
        print(f"更新表结构时出错: {e}")
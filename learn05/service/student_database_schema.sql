-- 学生数据库表结构设计
-- 学生表，存储学生基本信息
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('男', '女', '其他')),
    birth_date DATE,
    admission_date DATE,
    class_id INTEGER,
    contact_number TEXT,
    email TEXT UNIQUE,
    address TEXT,
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);

-- 班级表，存储班级信息
CREATE TABLE IF NOT EXISTS classes (
    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL UNIQUE,
    grade INTEGER NOT NULL,
    homeroom_teacher_id INTEGER,
    academic_year TEXT NOT NULL,
    FOREIGN KEY (homeroom_teacher_id) REFERENCES teachers(teacher_id)
);

-- 教师表，存储教师信息
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_name TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('男', '女', '其他')),
    contact_number TEXT,
    email TEXT UNIQUE,
    subject_id INTEGER,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- 科目表，存储课程科目信息
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT NOT NULL UNIQUE,
    credit INTEGER NOT NULL
);

-- 成绩表，存储学生成绩信息
CREATE TABLE IF NOT EXISTS grades (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    exam_date DATE NOT NULL,
    score REAL CHECK(score BETWEEN 0 AND 100),
    exam_type TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- 课程表，存储课程安排信息
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    schedule TEXT NOT NULL,
    location TEXT,
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
);

-- 考勤表，存储学生考勤信息
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    attendance_date DATE NOT NULL,
    status TEXT CHECK(status IN ('出勤', '缺勤', '请假')),
    reason TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- 课堂表现表，存储学生课堂表现信息
CREATE TABLE IF NOT EXISTS class_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    date DATE NOT NULL,
    participation_score INTEGER CHECK(participation_score BETWEEN 0 AND 100),
    comments TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
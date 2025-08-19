import 'dart:io';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/student_model.dart';
import '../models/grade_model.dart';
import '../utils/app_logger.dart';

class DatabaseService {
  static Database? _database;
  static const String _databaseName = 'smart_teaching_assistant.db';
  static const int _databaseVersion = 1;

  // 表名
  static const String _studentsTable = 'students';
  static const String _classesTable = 'classes';
  static const String _gradesTable = 'grades';
  static const String _examsTable = 'exams';
  static const String _subjectsTable = 'subjects';
  static const String _syncStatusTable = 'sync_status';

  static Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  static Future<Database> _initDatabase() async {
    try {
      final databasesPath = await getDatabasesPath();
      final path = join(databasesPath, _databaseName);

      AppLogger.info('Initializing database at: $path');

      return await openDatabase(
        path,
        version: _databaseVersion,
        onCreate: _onCreate,
        onUpgrade: _onUpgrade,
      );
    } catch (e, stackTrace) {
      AppLogger.error('Failed to initialize database', e, stackTrace);
      rethrow;
    }
  }

  static Future<void> _onCreate(Database db, int version) async {
    try {
      AppLogger.info('Creating database tables');

      // 创建学生表
      await db.execute('''
        CREATE TABLE $_studentsTable (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          student_number TEXT UNIQUE NOT NULL,
          class_id TEXT,
          grade_level TEXT,
          gender TEXT,
          birth_date TEXT,
          phone TEXT,
          email TEXT,
          address TEXT,
          parent_name TEXT,
          parent_phone TEXT,
          enrollment_date TEXT,
          status TEXT DEFAULT 'active',
          avatar_url TEXT,
          created_at TEXT,
          updated_at TEXT,
          is_synced INTEGER DEFAULT 0,
          last_sync_at TEXT
        )
      ''');

      // 创建班级表
      await db.execute('''
        CREATE TABLE $_classesTable (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          grade_level TEXT NOT NULL,
          teacher_id TEXT,
          teacher_name TEXT,
          academic_year TEXT,
          semester TEXT,
          description TEXT,
          student_count INTEGER DEFAULT 0,
          status TEXT DEFAULT 'active',
          created_at TEXT,
          updated_at TEXT,
          is_synced INTEGER DEFAULT 0,
          last_sync_at TEXT
        )
      ''');

      // 创建成绩表
      await db.execute('''
        CREATE TABLE $_gradesTable (
          id TEXT PRIMARY KEY,
          student_id TEXT NOT NULL,
          exam_id TEXT NOT NULL,
          subject_id TEXT NOT NULL,
          score REAL NOT NULL,
          full_score REAL DEFAULT 100,
          rank_in_class INTEGER,
          rank_in_grade INTEGER,
          percentile REAL,
          remark TEXT,
          created_at TEXT,
          updated_at TEXT,
          is_synced INTEGER DEFAULT 0,
          last_sync_at TEXT,
          FOREIGN KEY (student_id) REFERENCES $_studentsTable (id),
          FOREIGN KEY (exam_id) REFERENCES $_examsTable (id),
          FOREIGN KEY (subject_id) REFERENCES $_subjectsTable (id)
        )
      ''');

      // 创建考试表
      await db.execute('''
        CREATE TABLE $_examsTable (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          description TEXT,
          class_id TEXT,
          exam_date TEXT NOT NULL,
          exam_type TEXT,
          status TEXT DEFAULT 'scheduled',
          total_score REAL DEFAULT 100,
          duration_minutes INTEGER,
          created_at TEXT,
          updated_at TEXT,
          is_synced INTEGER DEFAULT 0,
          last_sync_at TEXT,
          FOREIGN KEY (class_id) REFERENCES $_classesTable (id)
        )
      ''');

      // 创建科目表
      await db.execute('''
        CREATE TABLE $_subjectsTable (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          code TEXT UNIQUE,
          description TEXT,
          color TEXT,
          icon TEXT,
          order_index INTEGER DEFAULT 0,
          is_active INTEGER DEFAULT 1,
          created_at TEXT,
          updated_at TEXT,
          is_synced INTEGER DEFAULT 0,
          last_sync_at TEXT
        )
      ''');

      // 创建同步状态表
      await db.execute('''
        CREATE TABLE $_syncStatusTable (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          table_name TEXT NOT NULL,
          record_id TEXT NOT NULL,
          operation TEXT NOT NULL, -- 'create', 'update', 'delete'
          data TEXT, -- JSON格式的数据
          sync_status TEXT DEFAULT 'pending', -- 'pending', 'syncing', 'synced', 'failed'
          retry_count INTEGER DEFAULT 0,
          error_message TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT,
          UNIQUE(table_name, record_id, operation)
        )
      ''');

      // 创建索引
      await db.execute('CREATE INDEX idx_students_class_id ON $_studentsTable (class_id)');
      await db.execute('CREATE INDEX idx_students_student_number ON $_studentsTable (student_number)');
      await db.execute('CREATE INDEX idx_grades_student_id ON $_gradesTable (student_id)');
      await db.execute('CREATE INDEX idx_grades_exam_id ON $_gradesTable (exam_id)');
      await db.execute('CREATE INDEX idx_grades_subject_id ON $_gradesTable (subject_id)');
      await db.execute('CREATE INDEX idx_exams_class_id ON $_examsTable (class_id)');
      await db.execute('CREATE INDEX idx_sync_status_table_record ON $_syncStatusTable (table_name, record_id)');
      await db.execute('CREATE INDEX idx_sync_status_status ON $_syncStatusTable (sync_status)');

      AppLogger.info('Database tables created successfully');
    } catch (e, stackTrace) {
      AppLogger.error('Failed to create database tables', e, stackTrace);
      rethrow;
    }
  }

  static Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    AppLogger.info('Upgrading database from version $oldVersion to $newVersion');
    // 在这里处理数据库升级逻辑
  }

  // 学生相关操作
  static Future<void> insertStudent(Student student) async {
    final db = await database;
    try {
      AppLogger.debug('插入学生数据开始: ${student.id}', {
        'name': student.name,
        'classId': student.classId,
        'studentNumber': student.studentNumber,
      });
      
      final studentData = student.toJson()..addAll({
        'is_synced': 0,
        'last_sync_at': null,
      });
      
      await db.insert(
        _studentsTable,
        studentData,
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
      
      AppLogger.info('学生数据插入成功: ${student.id} - ${student.name}');
    } catch (e, stackTrace) {
      AppLogger.error('插入学生数据失败: ${student.id} [${e.runtimeType}] Name: ${student.name}', e, stackTrace);
      rethrow;
    }
  }

  static Future<List<Student>> getStudents({String? classId}) async {
    final db = await database;
    try {
      AppLogger.debug('查询学生数据开始', {
        'classId': classId,
        'hasClassFilter': classId != null,
      });
      
      final List<Map<String, dynamic>> maps;
      if (classId != null) {
        maps = await db.query(
          _studentsTable,
          where: 'class_id = ?',
          whereArgs: [classId],
          orderBy: 'name ASC',
        );
      } else {
        maps = await db.query(
          _studentsTable,
          orderBy: 'name ASC',
        );
      }
      
      final students = maps.map((map) => Student.fromJson(map)).toList();
      
      AppLogger.debug('学生数据查询完成', {
        'resultCount': students.length,
        'classId': classId,
      });
      
      return students;
    } catch (e, stackTrace) {
      AppLogger.error('查询学生数据失败 [${e.runtimeType}] ClassId: $classId', e, stackTrace);
      rethrow;
    }
  }

  static Future<Student?> getStudentById(String id) async {
    final db = await database;
    try {
      AppLogger.debug('根据ID查询学生数据开始: $id');
      
      final maps = await db.query(
        _studentsTable,
        where: 'id = ?',
        whereArgs: [id],
        limit: 1,
      );
      
      if (maps.isNotEmpty) {
        final student = Student.fromJson(maps.first);
        AppLogger.debug('学生数据查询成功: $id - ${student.name}');
        return student;
      }
      AppLogger.debug('学生数据未找到: $id');
      return null;
    } catch (e, stackTrace) {
      AppLogger.error('根据ID查询学生数据失败 [${e.runtimeType}] StudentId: $id', e, stackTrace);
      rethrow;
    }
  }



  static Future<void> updateStudent(String studentId, Map<String, dynamic> updateData) async {
    final db = await database;
    try {
      AppLogger.debug('更新学生数据开始: $studentId', {
        'updateFields': updateData.keys.toList(),
        'fieldCount': updateData.length,
      });
      
      final finalUpdateData = Map<String, dynamic>.from(updateData)..addAll({
        'is_synced': 0,
        'updated_at': DateTime.now().toIso8601String(),
      });
      
      final rowsAffected = await db.update(
        _studentsTable,
        finalUpdateData,
        where: 'id = ?',
        whereArgs: [studentId],
      );
      
      AppLogger.info('学生数据更新成功: $studentId (影响行数: $rowsAffected)');
    } catch (e, stackTrace) {
      AppLogger.error('更新学生数据失败 [${e.runtimeType}] StudentId: $studentId, Fields: ${updateData.keys.join(", ")}', e, stackTrace);
      rethrow;
    }
  }

  static Future<void> deleteStudent(String id) async {
    final db = await database;
    try {
      AppLogger.debug('删除学生数据开始: $id');
      
      final rowsAffected = await db.delete(
        _studentsTable,
        where: 'id = ?',
        whereArgs: [id],
      );
      
      AppLogger.info('学生数据删除成功: $id (影响行数: $rowsAffected)');
    } catch (e, stackTrace) {
      AppLogger.error('删除学生数据失败 [${e.runtimeType}] StudentId: $id', e, stackTrace);
      rethrow;
    }
  }

  // 班级相关操作
  static Future<void> insertClass(Map<String, dynamic> classData) async {
    final db = await database;
    try {
      AppLogger.debug('插入班级数据开始: ${classData['id']}', {
        'name': classData['name'],
        'gradeLevel': classData['grade_level'],
        'teacherId': classData['teacher_id'],
      });
      
      final finalClassData = Map<String, dynamic>.from(classData)..addAll({
        'is_synced': 0,
        'last_sync_at': null,
      });
      
      await db.insert(
        _classesTable,
        finalClassData,
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
      
      AppLogger.info('班级数据插入成功: ${classData['id']} - ${classData['name']}');
    } catch (e, stackTrace) {
      AppLogger.error('插入班级数据失败 [${e.runtimeType}] ClassId: ${classData['id']}, Name: ${classData['name']}', e, stackTrace);
      rethrow;
    }
  }

  static Future<List<Map<String, dynamic>>> getClasses() async {
    final db = await database;
    try {
      AppLogger.debug('查询班级数据开始');
      
      final maps = await db.query(
        _classesTable,
        orderBy: 'grade_level ASC, name ASC',
      );
      
      AppLogger.debug('班级数据查询完成', {
        'resultCount': maps.length,
      });
      
      return maps;
    } catch (e, stackTrace) {
      AppLogger.error('查询班级数据失败 [${e.runtimeType}]', e, stackTrace);
      rethrow;
    }
  }

  // 成绩相关操作
  static Future<void> insertGrade(Grade grade) async {
    final db = await database;
    try {
      AppLogger.debug('插入成绩数据开始: ${grade.id}', {
        'studentId': grade.studentId,
        'examId': grade.examId,
        'subjectId': grade.subjectId,
        'score': grade.score,
      });
      
      final gradeData = grade.toJson()..addAll({
        'is_synced': 0,
        'last_sync_at': null,
      });
      
      await db.insert(
        _gradesTable,
        gradeData,
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
      
      AppLogger.info('成绩数据插入成功: ${grade.id} (学生: ${grade.studentId}, 分数: ${grade.score})');
    } catch (e, stackTrace) {
      AppLogger.error('插入成绩数据失败 [${e.runtimeType}] GradeId: ${grade.id}, StudentId: ${grade.studentId}, Score: ${grade.score}', e, stackTrace);
      rethrow;
    }
  }

  static Future<List<Grade>> getGrades({
    String? studentId,
    String? examId,
    String? subjectId,
  }) async {
    final db = await database;
    try {
      AppLogger.debug('查询成绩数据开始', {
        'studentId': studentId,
        'examId': examId,
        'subjectId': subjectId,
      });
      
      String whereClause = '';
      List<dynamic> whereArgs = [];

      if (studentId != null) {
        whereClause += 'student_id = ?';
        whereArgs.add(studentId);
      }

      if (examId != null) {
        if (whereClause.isNotEmpty) whereClause += ' AND ';
        whereClause += 'exam_id = ?';
        whereArgs.add(examId);
      }

      if (subjectId != null) {
        if (whereClause.isNotEmpty) whereClause += ' AND ';
        whereClause += 'subject_id = ?';
        whereArgs.add(subjectId);
      }

      final maps = await db.query(
        _gradesTable,
        where: whereClause.isNotEmpty ? whereClause : null,
        whereArgs: whereArgs.isNotEmpty ? whereArgs : null,
        orderBy: 'created_at DESC',
      );
      
      final grades = maps.map((map) => Grade.fromJson(map)).toList();
      
      AppLogger.debug('成绩数据查询完成', {
        'resultCount': grades.length,
        'filters': {
          'studentId': studentId,
          'examId': examId,
          'subjectId': subjectId,
        },
      });
      
      return grades;
    } catch (e, stackTrace) {
      AppLogger.error('查询成绩数据失败 [${e.runtimeType}] Filters - StudentId: $studentId, ExamId: $examId, SubjectId: $subjectId', e, stackTrace);
      rethrow;
    }
  }

  // 同步状态相关操作
  static Future<void> addSyncRecord({
    required String tableName,
    required String recordId,
    required String operation,
    Map<String, dynamic>? data,
  }) async {
    final db = await database;
    try {
      AppLogger.debug('添加同步记录开始', {
        'tableName': tableName,
        'recordId': recordId,
        'operation': operation,
        'hasData': data != null,
      });
      
      await db.insert(
        _syncStatusTable,
        {
          'table_name': tableName,
          'record_id': recordId,
          'operation': operation,
          'data': data != null ? data.toString() : null,
          'sync_status': 'pending',
          'retry_count': 0,
          'created_at': DateTime.now().toIso8601String(),
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
      
      AppLogger.info('同步记录添加成功: $tableName/$recordId/$operation');
    } catch (e, stackTrace) {
      AppLogger.error('添加同步记录失败 [${e.runtimeType}] Table: $tableName, RecordId: $recordId, Operation: $operation', e, stackTrace);
      rethrow;
    }
  }

  static Future<List<Map<String, dynamic>>> getPendingSyncRecords() async {
    final db = await database;
    try {
      AppLogger.debug('查询待同步记录开始');
      
      final records = await db.query(
        _syncStatusTable,
        where: 'sync_status = ?',
        whereArgs: ['pending'],
        orderBy: 'created_at ASC',
      );
      
      AppLogger.debug('待同步记录查询完成', {
        'pendingCount': records.length,
      });
      
      return records;
    } catch (e, stackTrace) {
      AppLogger.error('查询待同步记录失败 [${e.runtimeType}]', e, stackTrace);
      rethrow;
    }
  }

  static Future<void> updateSyncStatus({
    required int syncId,
    required String status,
    String? errorMessage,
  }) async {
    final db = await database;
    try {
      AppLogger.debug('更新同步状态开始', {
        'syncId': syncId,
        'status': status,
        'hasErrorMessage': errorMessage != null,
      });
      
      final rowsAffected = await db.update(
        _syncStatusTable,
        {
          'sync_status': status,
          'error_message': errorMessage,
          'updated_at': DateTime.now().toIso8601String(),
        },
        where: 'id = ?',
        whereArgs: [syncId],
      );
      
      AppLogger.info('同步状态更新成功: $syncId -> $status (影响行数: $rowsAffected)');
    } catch (e, stackTrace) {
      AppLogger.error('更新同步状态失败 [${e.runtimeType}] SyncId: $syncId, Status: $status', e, stackTrace);
      rethrow;
    }
  }

  // 清理数据
  static Future<void> clearAllData() async {
    final db = await database;
    try {
      AppLogger.debug('清空所有数据开始');
      
      final studentsDeleted = await db.delete(_studentsTable);
      final classesDeleted = await db.delete(_classesTable);
      final gradesDeleted = await db.delete(_gradesTable);
      final examsDeleted = await db.delete(_examsTable);
      final subjectsDeleted = await db.delete(_subjectsTable);
      final syncStatusDeleted = await db.delete(_syncStatusTable);
      
      AppLogger.info('所有数据清空成功', {
        'studentsDeleted': studentsDeleted,
        'classesDeleted': classesDeleted,
        'gradesDeleted': gradesDeleted,
        'examsDeleted': examsDeleted,
        'subjectsDeleted': subjectsDeleted,
        'syncStatusDeleted': syncStatusDeleted,
      });
    } catch (e, stackTrace) {
      AppLogger.error('清空所有数据失败 [${e.runtimeType}]', e, stackTrace);
      rethrow;
    }
  }

  // 关闭数据库
  static Future<void> close() async {
    try {
      if (_database != null) {
        AppLogger.debug('关闭数据库连接开始');
        await _database!.close();
        _database = null;
        AppLogger.info('数据库连接关闭成功');
      } else {
        AppLogger.debug('数据库连接已经关闭或未初始化');
      }
    } catch (e, stackTrace) {
      AppLogger.error('关闭数据库连接失败 [${e.runtimeType}]', e, stackTrace);
      rethrow;
    }
  }



  // 获取数据库大小
  static Future<int> getDatabaseSize() async {
    try {
      final dbPath = await getDatabasesPath();
      final file = File(join(dbPath, _databaseName));
      if (await file.exists()) {
        final stat = await file.stat();
        return stat.size;
      }
      return 0;
    } catch (e, stackTrace) {
      AppLogger.error('Failed to get database size', e, stackTrace);
      return 0;
    }
  }

  // 释放资源
  static Future<void> dispose() async {
    await close();
  }
}
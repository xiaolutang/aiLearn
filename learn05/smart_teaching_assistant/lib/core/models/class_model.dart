// 班级数据模型
class SchoolClass {
  final String id;
  final String name;
  final String grade;
  final String? description;
  final String teacherId;
  final String? teacherName;
  final int studentCount;
  final String academicYear;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? settings;

  const SchoolClass({
    required this.id,
    required this.name,
    required this.grade,
    this.description,
    required this.teacherId,
    this.teacherName,
    required this.studentCount,
    required this.academicYear,
    required this.createdAt,
    required this.updatedAt,
    this.settings,
  });

  factory SchoolClass.fromJson(Map<String, dynamic> json) {
    return SchoolClass(
      id: json['id'] as String,
      name: json['name'] as String,
      grade: json['grade'] as String,
      description: json['description'] as String?,
      teacherId: json['teacher_id'] as String,
      teacherName: json['teacher_name'] as String?,
      studentCount: json['student_count'] as int? ?? 0,
      academicYear: json['academic_year'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      settings: json['settings'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'grade': grade,
      'description': description,
      'teacher_id': teacherId,
      'teacher_name': teacherName,
      'student_count': studentCount,
      'academic_year': academicYear,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'settings': settings,
    };
  }

  SchoolClass copyWith({
    String? id,
    String? name,
    String? grade,
    String? description,
    String? teacherId,
    String? teacherName,
    int? studentCount,
    String? academicYear,
    DateTime? createdAt,
    DateTime? updatedAt,
    Map<String, dynamic>? settings,
  }) {
    return SchoolClass(
      id: id ?? this.id,
      name: name ?? this.name,
      grade: grade ?? this.grade,
      description: description ?? this.description,
      teacherId: teacherId ?? this.teacherId,
      teacherName: teacherName ?? this.teacherName,
      studentCount: studentCount ?? this.studentCount,
      academicYear: academicYear ?? this.academicYear,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      settings: settings ?? this.settings,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is SchoolClass && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'SchoolClass(id: $id, name: $name, grade: $grade, studentCount: $studentCount)';
  }
}
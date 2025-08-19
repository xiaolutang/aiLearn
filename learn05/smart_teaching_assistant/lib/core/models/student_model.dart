// 学生数据模型
class Student {
  final String id;
  final String name;
  final String studentNumber;
  final String? email;
  final String? phone;
  final String? avatar;
  final String? classId;
  final String? className;
  final String? grade;
  final String? gender;
  final DateTime? birthDate;
  final String? address;
  final String? parentName;
  final String? parentPhone;
  final String? parentEmail;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final bool isActive;

  const Student({
    required this.id,
    required this.name,
    required this.studentNumber,
    this.email,
    this.phone,
    this.avatar,
    this.classId,
    this.className,
    this.grade,
    this.gender,
    this.birthDate,
    this.address,
    this.parentName,
    this.parentPhone,
    this.parentEmail,
    this.metadata,
    required this.createdAt,
    this.updatedAt,
    this.isActive = true,
  });

  factory Student.fromJson(Map<String, dynamic> json) {
    return Student(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      studentNumber: json['student_number'] ?? '',
      email: json['email'],
      phone: json['phone'],
      avatar: json['avatar'],
      classId: json['class_id'],
      className: json['class_name'],
      grade: json['grade'],
      gender: json['gender'],
      birthDate: json['birth_date'] != null ? DateTime.parse(json['birth_date']) : null,
      address: json['address'],
      parentName: json['parent_name'],
      parentPhone: json['parent_phone'],
      parentEmail: json['parent_email'],
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'student_number': studentNumber,
      'email': email,
      'phone': phone,
      'avatar': avatar,
      'class_id': classId,
      'class_name': className,
      'grade': grade,
      'gender': gender,
      'birth_date': birthDate?.toIso8601String(),
      'address': address,
      'parent_name': parentName,
      'parent_phone': parentPhone,
      'parent_email': parentEmail,
      'metadata': metadata,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'is_active': isActive,
    };
  }

  Student copyWith({
    String? id,
    String? name,
    String? studentNumber,
    String? email,
    String? phone,
    String? avatar,
    String? classId,
    String? className,
    String? grade,
    String? gender,
    DateTime? birthDate,
    String? address,
    String? parentName,
    String? parentPhone,
    String? parentEmail,
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? isActive,
  }) {
    return Student(
      id: id ?? this.id,
      name: name ?? this.name,
      studentNumber: studentNumber ?? this.studentNumber,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      avatar: avatar ?? this.avatar,
      classId: classId ?? this.classId,
      className: className ?? this.className,
      grade: grade ?? this.grade,
      gender: gender ?? this.gender,
      birthDate: birthDate ?? this.birthDate,
      address: address ?? this.address,
      parentName: parentName ?? this.parentName,
      parentPhone: parentPhone ?? this.parentPhone,
      parentEmail: parentEmail ?? this.parentEmail,
      metadata: metadata ?? this.metadata,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      isActive: isActive ?? this.isActive,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Student && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'Student(id: $id, name: $name, studentNumber: $studentNumber, classId: $classId)';
  }
}
import 'package:json_annotation/json_annotation.dart';

part 'user_model.g.dart';

/// 用户模型
@JsonSerializable()
class UserModel {
  @JsonKey(name: 'id')
  final int id;
  
  @JsonKey(name: 'username')
  final String username;
  
  @JsonKey(name: 'email')
  final String? email;
  
  @JsonKey(name: 'phone')
  final String? phone;
  
  @JsonKey(name: 'full_name')
  final String? fullName;
  
  @JsonKey(name: 'avatar_url')
  final String? avatarUrl;
  
  @JsonKey(name: 'role')
  final UserRole role;
  
  @JsonKey(name: 'is_active')
  final bool isActive;
  
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;
  
  @JsonKey(name: 'last_login')
  final DateTime? lastLogin;
  
  @JsonKey(name: 'profile')
  final UserProfile? profile;

  const UserModel({
    required this.id,
    required this.username,
    this.email,
    this.phone,
    this.fullName,
    this.avatarUrl,
    required this.role,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
    this.lastLogin,
    this.profile,
  });

  /// 从JSON创建用户模型
  factory UserModel.fromJson(Map<String, dynamic> json) => _$UserModelFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$UserModelToJson(this);

  /// 复制并更新部分字段
  UserModel copyWith({
    int? id,
    String? username,
    String? email,
    String? phone,
    String? fullName,
    String? avatarUrl,
    UserRole? role,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? lastLogin,
    UserProfile? profile,
  }) {
    return UserModel(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      fullName: fullName ?? this.fullName,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      role: role ?? this.role,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      lastLogin: lastLogin ?? this.lastLogin,
      profile: profile ?? this.profile,
    );
  }

  /// 获取显示名称
  String get displayName {
    if (fullName != null && fullName!.isNotEmpty) {
      return fullName!;
    }
    return username;
  }

  /// 获取头像URL或默认头像
  String get avatarUrlOrDefault {
    return avatarUrl ?? 'https://via.placeholder.com/150';
  }

  /// 是否为教师
  bool get isTeacher => role == UserRole.teacher;

  /// 是否为学生
  bool get isStudent => role == UserRole.student;

  /// 是否为家长
  bool get isParent => role == UserRole.parent;

  /// 是否为管理员
  bool get isAdmin => role == UserRole.admin;

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is UserModel && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'UserModel(id: $id, username: $username, role: $role)';
  }
}

/// 用户角色枚举
@JsonEnum()
enum UserRole {
  @JsonValue('teacher')
  teacher,
  
  @JsonValue('student')
  student,
  
  @JsonValue('parent')
  parent,
  
  @JsonValue('admin')
  admin,
}

/// 用户角色扩展
extension UserRoleExtension on UserRole {
  /// 获取角色显示名称
  String get displayName {
    switch (this) {
      case UserRole.teacher:
        return '教师';
      case UserRole.student:
        return '学生';
      case UserRole.parent:
        return '家长';
      case UserRole.admin:
        return '管理员';
    }
  }

  /// 获取角色图标
  String get iconName {
    switch (this) {
      case UserRole.teacher:
        return 'school';
      case UserRole.student:
        return 'person';
      case UserRole.parent:
        return 'family_restroom';
      case UserRole.admin:
        return 'admin_panel_settings';
    }
  }
}

/// 用户资料模型
@JsonSerializable()
class UserProfile {
  @JsonKey(name: 'bio')
  final String? bio;
  
  @JsonKey(name: 'school_name')
  final String? schoolName;
  
  @JsonKey(name: 'grade')
  final String? grade;
  
  @JsonKey(name: 'class_name')
  final String? className;
  
  @JsonKey(name: 'subject')
  final String? subject;
  
  @JsonKey(name: 'student_id')
  final String? studentId;
  
  @JsonKey(name: 'teacher_id')
  final String? teacherId;
  
  @JsonKey(name: 'birth_date')
  final DateTime? birthDate;
  
  @JsonKey(name: 'gender')
  final Gender? gender;
  
  @JsonKey(name: 'address')
  final String? address;
  
  @JsonKey(name: 'emergency_contact')
  final String? emergencyContact;
  
  @JsonKey(name: 'preferences')
  final Map<String, dynamic>? preferences;

  const UserProfile({
    this.bio,
    this.schoolName,
    this.grade,
    this.className,
    this.subject,
    this.studentId,
    this.teacherId,
    this.birthDate,
    this.gender,
    this.address,
    this.emergencyContact,
    this.preferences,
  });

  /// 从JSON创建用户资料
  factory UserProfile.fromJson(Map<String, dynamic> json) => _$UserProfileFromJson(json);

  /// 转换为JSON
  Map<String, dynamic> toJson() => _$UserProfileToJson(this);

  /// 复制并更新部分字段
  UserProfile copyWith({
    String? bio,
    String? schoolName,
    String? grade,
    String? className,
    String? subject,
    String? studentId,
    String? teacherId,
    DateTime? birthDate,
    Gender? gender,
    String? address,
    String? emergencyContact,
    Map<String, dynamic>? preferences,
  }) {
    return UserProfile(
      bio: bio ?? this.bio,
      schoolName: schoolName ?? this.schoolName,
      grade: grade ?? this.grade,
      className: className ?? this.className,
      subject: subject ?? this.subject,
      studentId: studentId ?? this.studentId,
      teacherId: teacherId ?? this.teacherId,
      birthDate: birthDate ?? this.birthDate,
      gender: gender ?? this.gender,
      address: address ?? this.address,
      emergencyContact: emergencyContact ?? this.emergencyContact,
      preferences: preferences ?? this.preferences,
    );
  }
}

/// 性别枚举
@JsonEnum()
enum Gender {
  @JsonValue('male')
  male,
  
  @JsonValue('female')
  female,
  
  @JsonValue('other')
  other,
}

/// 性别扩展
extension GenderExtension on Gender {
  /// 获取性别显示名称
  String get displayName {
    switch (this) {
      case Gender.male:
        return '男';
      case Gender.female:
        return '女';
      case Gender.other:
        return '其他';
    }
  }
}
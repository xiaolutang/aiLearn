// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserModel _$UserModelFromJson(Map<String, dynamic> json) => UserModel(
      id: json['id'] as int,
      username: json['username'] as String,
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      fullName: json['full_name'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      role: $enumDecode(_$UserRoleEnumMap, json['role']),
      isActive: json['is_active'] as bool,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      lastLogin: json['last_login'] == null
          ? null
          : DateTime.parse(json['last_login'] as String),
      profile: json['profile'] == null
          ? null
          : UserProfile.fromJson(json['profile'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$UserModelToJson(UserModel instance) => <String, dynamic>{
      'id': instance.id,
      'username': instance.username,
      'email': instance.email,
      'phone': instance.phone,
      'full_name': instance.fullName,
      'avatar_url': instance.avatarUrl,
      'role': _$UserRoleEnumMap[instance.role]!,
      'is_active': instance.isActive,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
      'last_login': instance.lastLogin?.toIso8601String(),
      'profile': instance.profile,
    };

const _$UserRoleEnumMap = {
  UserRole.teacher: 'teacher',
  UserRole.student: 'student',
  UserRole.parent: 'parent',
  UserRole.admin: 'admin',
};

UserProfile _$UserProfileFromJson(Map<String, dynamic> json) => UserProfile(
      bio: json['bio'] as String?,
      schoolName: json['school_name'] as String?,
      grade: json['grade'] as String?,
      className: json['class_name'] as String?,
      subject: json['subject'] as String?,
      studentId: json['student_id'] as String?,
      teacherId: json['teacher_id'] as String?,
      birthDate: json['birth_date'] == null
          ? null
          : DateTime.parse(json['birth_date'] as String),
      gender: $enumDecodeNullable(_$GenderEnumMap, json['gender']),
      address: json['address'] as String?,
      emergencyContact: json['emergency_contact'] as String?,
      preferences: json['preferences'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$UserProfileToJson(UserProfile instance) =>
    <String, dynamic>{
      'bio': instance.bio,
      'school_name': instance.schoolName,
      'grade': instance.grade,
      'class_name': instance.className,
      'subject': instance.subject,
      'student_id': instance.studentId,
      'teacher_id': instance.teacherId,
      'birth_date': instance.birthDate?.toIso8601String(),
      'gender': _$GenderEnumMap[instance.gender],
      'address': instance.address,
      'emergency_contact': instance.emergencyContact,
      'preferences': instance.preferences,
    };

const _$GenderEnumMap = {
  Gender.male: 'male',
  Gender.female: 'female',
  Gender.other: 'other',
};

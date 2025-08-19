import 'package:json_annotation/json_annotation.dart';
import 'api_response.dart';

part 'auth_models.g.dart';

/// 登录请求模型
@JsonSerializable()
class LoginRequest {
  final String username;
  final String password;
  @JsonKey(name: 'remember_me')
  final bool? rememberMe;
  
  const LoginRequest({
    required this.username,
    required this.password,
    this.rememberMe,
  });
  
  factory LoginRequest.fromJson(Map<String, dynamic> json) => _$LoginRequestFromJson(json);
  Map<String, dynamic> toJson() => _$LoginRequestToJson(this);
}

/// 注册请求模型
@JsonSerializable()
class RegisterRequest {
  final String name;
  final String email;
  final String password;
  @JsonKey(name: 'password_confirmation')
  final String? passwordConfirmation;
  final String? role;
  final String? phone;
  final String? avatar;
  
  const RegisterRequest({
    required this.name,
    required this.email,
    required this.password,
    this.passwordConfirmation,
    this.role,
    this.phone,
    this.avatar,
  });
  
  factory RegisterRequest.fromJson(Map<String, dynamic> json) => _$RegisterRequestFromJson(json);
  Map<String, dynamic> toJson() => _$RegisterRequestToJson(this);
}

/// 登录响应模型
@JsonSerializable()
class LoginResponse {
  @JsonKey(name: 'access_token')
  final String accessToken;
  @JsonKey(name: 'refresh_token')
  final String? refreshToken;
  @JsonKey(name: 'token_type')
  final String tokenType;
  @JsonKey(name: 'expires_in')
  final int expiresIn;
  final Map<String, dynamic> user;
  
  const LoginResponse({
    required this.accessToken,
    this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });
  
  factory LoginResponse.fromJson(Map<String, dynamic> json) => _$LoginResponseFromJson(json);
  Map<String, dynamic> toJson() => _$LoginResponseToJson(this);
}

/// 刷新Token请求模型
@JsonSerializable()
class RefreshTokenRequest {
  @JsonKey(name: 'refresh_token')
  final String refreshToken;
  
  const RefreshTokenRequest({
    required this.refreshToken,
  });
  
  factory RefreshTokenRequest.fromJson(Map<String, dynamic> json) => _$RefreshTokenRequestFromJson(json);
  Map<String, dynamic> toJson() => _$RefreshTokenRequestToJson(this);
}

/// 修改密码请求模型
@JsonSerializable()
class ChangePasswordRequest {
  @JsonKey(name: 'current_password')
  final String currentPassword;
  @JsonKey(name: 'new_password')
  final String newPassword;
  @JsonKey(name: 'new_password_confirmation')
  final String? newPasswordConfirmation;
  
  const ChangePasswordRequest({
    required this.currentPassword,
    required this.newPassword,
    this.newPasswordConfirmation,
  });
  
  factory ChangePasswordRequest.fromJson(Map<String, dynamic> json) => _$ChangePasswordRequestFromJson(json);
  Map<String, dynamic> toJson() => _$ChangePasswordRequestToJson(this);
}

/// 忘记密码请求模型
@JsonSerializable()
class ForgotPasswordRequest {
  final String email;
  
  const ForgotPasswordRequest({
    required this.email,
  });
  
  factory ForgotPasswordRequest.fromJson(Map<String, dynamic> json) => _$ForgotPasswordRequestFromJson(json);
  Map<String, dynamic> toJson() => _$ForgotPasswordRequestToJson(this);
}

/// 重置密码请求模型
@JsonSerializable()
class ResetPasswordRequest {
  final String token;
  final String email;
  final String password;
  @JsonKey(name: 'password_confirmation')
  final String passwordConfirmation;
  
  const ResetPasswordRequest({
    required this.token,
    required this.email,
    required this.password,
    required this.passwordConfirmation,
  });
  
  factory ResetPasswordRequest.fromJson(Map<String, dynamic> json) => _$ResetPasswordRequestFromJson(json);
  Map<String, dynamic> toJson() => _$ResetPasswordRequestToJson(this);
}

/// 更新用户资料请求模型
@JsonSerializable()
class UpdateProfileRequest {
  final String? name;
  final String? email;
  final String? phone;
  final String? avatar;
  final Map<String, dynamic>? profile;
  
  const UpdateProfileRequest({
    this.name,
    this.email,
    this.phone,
    this.avatar,
    this.profile,
  });
  
  factory UpdateProfileRequest.fromJson(Map<String, dynamic> json) => _$UpdateProfileRequestFromJson(json);
  Map<String, dynamic> toJson() => _$UpdateProfileRequestToJson(this);
}



/// 分页信息模型
@JsonSerializable()
class PaginationMeta {
  @JsonKey(name: 'current_page')
  final int currentPage;
  @JsonKey(name: 'last_page')
  final int lastPage;
  @JsonKey(name: 'per_page')
  final int perPage;
  final int total;
  final int from;
  final int to;
  
  const PaginationMeta({
    required this.currentPage,
    required this.lastPage,
    required this.perPage,
    required this.total,
    required this.from,
    required this.to,
  });
  
  factory PaginationMeta.fromJson(Map<String, dynamic> json) => _$PaginationMetaFromJson(json);
  Map<String, dynamic> toJson() => _$PaginationMetaToJson(this);
  
  /// 是否有下一页
  bool get hasNextPage => currentPage < lastPage;
  
  /// 是否有上一页
  bool get hasPreviousPage => currentPage > 1;
  
  /// 总页数
  int get totalPages => lastPage;
}

/// 分页响应模型
@JsonSerializable(genericArgumentFactories: true)
class PaginatedResponse<T> {
  final List<T> data;
  final PaginationMeta meta;
  
  const PaginatedResponse({
    required this.data,
    required this.meta,
  });
  
  factory PaginatedResponse.fromJson(
    Map<String, dynamic> json,
    T Function(Object? json) fromJsonT,
  ) => _$PaginatedResponseFromJson(json, fromJsonT);
  
  Map<String, dynamic> toJson(Object Function(T value) toJsonT) => _$PaginatedResponseToJson(this, toJsonT);
}
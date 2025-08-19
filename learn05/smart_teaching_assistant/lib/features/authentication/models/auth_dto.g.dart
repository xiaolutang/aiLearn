// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

LoginRequestDto _$LoginRequestDtoFromJson(Map<String, dynamic> json) =>
    LoginRequestDto(
      username: json['username'] as String,
      password: json['password'] as String,
      rememberMe: json['remember_me'] as bool? ?? false,
      deviceInfo: json['device_info'] == null
          ? null
          : DeviceInfoDto.fromJson(json['device_info'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$LoginRequestDtoToJson(LoginRequestDto instance) =>
    <String, dynamic>{
      'username': instance.username,
      'password': instance.password,
      'remember_me': instance.rememberMe,
      'device_info': instance.deviceInfo,
    };

LoginResponseDto _$LoginResponseDtoFromJson(Map<String, dynamic> json) =>
    LoginResponseDto(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      tokenType: json['token_type'] as String,
      expiresIn: json['expires_in'] as int,
      user: json['user'] as Map<String, dynamic>,
      permissions: (json['permissions'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      settings: json['settings'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$LoginResponseDtoToJson(LoginResponseDto instance) =>
    <String, dynamic>{
      'access_token': instance.accessToken,
      'refresh_token': instance.refreshToken,
      'token_type': instance.tokenType,
      'expires_in': instance.expiresIn,
      'user': instance.user,
      'permissions': instance.permissions,
      'settings': instance.settings,
    };

RegisterRequestDto _$RegisterRequestDtoFromJson(Map<String, dynamic> json) =>
    RegisterRequestDto(
      username: json['username'] as String,
      email: json['email'] as String,
      password: json['password'] as String,
      confirmPassword: json['confirm_password'] as String,
      fullName: json['full_name'] as String,
      role: json['role'] as String,
      phone: json['phone'] as String?,
      schoolCode: json['school_code'] as String?,
      invitationCode: json['invitation_code'] as String?,
      deviceInfo: json['device_info'] == null
          ? null
          : DeviceInfoDto.fromJson(json['device_info'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$RegisterRequestDtoToJson(RegisterRequestDto instance) =>
    <String, dynamic>{
      'username': instance.username,
      'email': instance.email,
      'password': instance.password,
      'confirm_password': instance.confirmPassword,
      'full_name': instance.fullName,
      'role': instance.role,
      'phone': instance.phone,
      'school_code': instance.schoolCode,
      'invitation_code': instance.invitationCode,
      'device_info': instance.deviceInfo,
    };

RegisterResponseDto _$RegisterResponseDtoFromJson(Map<String, dynamic> json) =>
    RegisterResponseDto(
      userId: json['user_id'] as int,
      username: json['username'] as String,
      email: json['email'] as String,
      message: json['message'] as String,
      verificationRequired: json['verification_required'] as bool,
      verificationMethod: json['verification_method'] as String?,
    );

Map<String, dynamic> _$RegisterResponseDtoToJson(
        RegisterResponseDto instance) =>
    <String, dynamic>{
      'user_id': instance.userId,
      'username': instance.username,
      'email': instance.email,
      'message': instance.message,
      'verification_required': instance.verificationRequired,
      'verification_method': instance.verificationMethod,
    };

RefreshTokenRequestDto _$RefreshTokenRequestDtoFromJson(
        Map<String, dynamic> json) =>
    RefreshTokenRequestDto(
      refreshToken: json['refresh_token'] as String,
      deviceInfo: json['device_info'] == null
          ? null
          : DeviceInfoDto.fromJson(json['device_info'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$RefreshTokenRequestDtoToJson(
        RefreshTokenRequestDto instance) =>
    <String, dynamic>{
      'refresh_token': instance.refreshToken,
      'device_info': instance.deviceInfo,
    };

RefreshTokenResponseDto _$RefreshTokenResponseDtoFromJson(
        Map<String, dynamic> json) =>
    RefreshTokenResponseDto(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String?,
      tokenType: json['token_type'] as String,
      expiresIn: json['expires_in'] as int,
    );

Map<String, dynamic> _$RefreshTokenResponseDtoToJson(
        RefreshTokenResponseDto instance) =>
    <String, dynamic>{
      'access_token': instance.accessToken,
      'refresh_token': instance.refreshToken,
      'token_type': instance.tokenType,
      'expires_in': instance.expiresIn,
    };

PasswordResetRequestDto _$PasswordResetRequestDtoFromJson(
        Map<String, dynamic> json) =>
    PasswordResetRequestDto(
      email: json['email'] as String,
      username: json['username'] as String?,
      captchaToken: json['captcha_token'] as String?,
    );

Map<String, dynamic> _$PasswordResetRequestDtoToJson(
        PasswordResetRequestDto instance) =>
    <String, dynamic>{
      'email': instance.email,
      'username': instance.username,
      'captcha_token': instance.captchaToken,
    };

PasswordResetConfirmDto _$PasswordResetConfirmDtoFromJson(
        Map<String, dynamic> json) =>
    PasswordResetConfirmDto(
      token: json['token'] as String,
      newPassword: json['new_password'] as String,
      confirmPassword: json['confirm_password'] as String,
    );

Map<String, dynamic> _$PasswordResetConfirmDtoToJson(
        PasswordResetConfirmDto instance) =>
    <String, dynamic>{
      'token': instance.token,
      'new_password': instance.newPassword,
      'confirm_password': instance.confirmPassword,
    };

DeviceInfoDto _$DeviceInfoDtoFromJson(Map<String, dynamic> json) =>
    DeviceInfoDto(
      deviceId: json['device_id'] as String,
      deviceName: json['device_name'] as String,
      platform: json['platform'] as String,
      osVersion: json['os_version'] as String,
      appVersion: json['app_version'] as String,
      screenResolution: json['screen_resolution'] as String?,
      timezone: json['timezone'] as String?,
      locale: json['locale'] as String?,
    );

Map<String, dynamic> _$DeviceInfoDtoToJson(DeviceInfoDto instance) =>
    <String, dynamic>{
      'device_id': instance.deviceId,
      'device_name': instance.deviceName,
      'platform': instance.platform,
      'os_version': instance.osVersion,
      'app_version': instance.appVersion,
      'screen_resolution': instance.screenResolution,
      'timezone': instance.timezone,
      'locale': instance.locale,
    };

VerificationCodeDto _$VerificationCodeDtoFromJson(Map<String, dynamic> json) =>
    VerificationCodeDto(
      code: json['code'] as String,
      type: $enumDecode(_$VerificationTypeEnumMap, json['type']),
      identifier: json['identifier'] as String,
      purpose: $enumDecode(_$VerificationPurposeEnumMap, json['purpose']),
    );

Map<String, dynamic> _$VerificationCodeDtoToJson(
        VerificationCodeDto instance) =>
    <String, dynamic>{
      'code': instance.code,
      'type': _$VerificationTypeEnumMap[instance.type]!,
      'identifier': instance.identifier,
      'purpose': _$VerificationPurposeEnumMap[instance.purpose]!,
    };

const _$VerificationTypeEnumMap = {
  VerificationType.email: 'email',
  VerificationType.sms: 'sms',
  VerificationType.voice: 'voice',
};

const _$VerificationPurposeEnumMap = {
  VerificationPurpose.registration: 'registration',
  VerificationPurpose.passwordReset: 'password_reset',
  VerificationPurpose.loginVerification: 'login_verification',
  VerificationPurpose.emailChange: 'email_change',
  VerificationPurpose.phoneChange: 'phone_change',
};

ThirdPartyLoginDto _$ThirdPartyLoginDtoFromJson(Map<String, dynamic> json) =>
    ThirdPartyLoginDto(
      provider: json['provider'] as String,
      accessToken: json['access_token'] as String,
      openId: json['open_id'] as String?,
      unionId: json['union_id'] as String?,
      userInfo: json['user_info'] as Map<String, dynamic>?,
      deviceInfo: json['device_info'] == null
          ? null
          : DeviceInfoDto.fromJson(json['device_info'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$ThirdPartyLoginDtoToJson(ThirdPartyLoginDto instance) =>
    <String, dynamic>{
      'provider': instance.provider,
      'access_token': instance.accessToken,
      'open_id': instance.openId,
      'union_id': instance.unionId,
      'user_info': instance.userInfo,
      'device_info': instance.deviceInfo,
    };

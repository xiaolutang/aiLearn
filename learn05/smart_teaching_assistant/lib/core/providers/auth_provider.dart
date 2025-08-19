import 'package:flutter/foundation.dart';
import '../data/repositories/auth_repository.dart';
import '../models/api_response.dart';
import '../utils/app_logger.dart';

/// 认证状态枚举
enum AuthStatus {
  initial,
  loading,
  authenticated,
  unauthenticated,
  error,
}

/// 认证状态管理器
class AuthProvider extends ChangeNotifier {
  final AuthRepository _authRepository;
  
  AuthProvider({required AuthRepository authRepository}) 
      : _authRepository = authRepository;

  // 状态变量
  AuthStatus _status = AuthStatus.initial;
  User? _currentUser;
  String? _errorMessage;
  bool _isLoading = false;
  bool _rememberMe = false;
  
  // Getters
  AuthStatus get status => _status;
  User? get currentUser => _currentUser;
  String? get errorMessage => _errorMessage;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _status == AuthStatus.authenticated && _currentUser != null;
  bool get isUnauthenticated => _status == AuthStatus.unauthenticated;
  bool get rememberMe => _rememberMe;
  
  // 用户角色相关
  bool get isTeacher => _currentUser?.isTeacher ?? false;
  bool get isStudent => _currentUser?.isStudent ?? false;
  bool get isAdmin => _currentUser?.isAdmin ?? false;
  
  // 权限检查
  bool hasPermission(String permission) {
    return _currentUser?.hasPermission(permission) ?? false;
  }

  // 兼容性属性（保持向后兼容）
  User? get user => _currentUser;

  /// 初始化认证状态
  Future<void> initialize() async {
    try {
      _setLoading(true);
      _clearError();
      
      // 检查是否已登录
      final isLoggedIn = await _authRepository.isLoggedIn();
      if (isLoggedIn) {
        // 获取本地用户信息
        final localUser = await _authRepository.getLocalUser();
        if (localUser != null) {
          _currentUser = localUser;
          _setStatus(AuthStatus.authenticated);
          
          // 尝试刷新用户信息
          _refreshUserInfo();
        } else {
          _setStatus(AuthStatus.unauthenticated);
        }
      } else {
        _setStatus(AuthStatus.unauthenticated);
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 初始化失败', e, stackTrace);
      _setError('初始化失败: ${e.toString()}');
      _setStatus(AuthStatus.error);
    } finally {
      _setLoading(false);
    }
  }

  /// 兼容性方法：初始化认证状态
  Future<void> initializeAuth() async {
    AppLogger.info('开始初始化认证状态');
    await initialize();
    AppLogger.info('认证状态初始化完成');
  }

  /// 用户登录
  Future<bool> login(
    String identifier,
    String password, {
    bool rememberMe = false,
    String? captcha,
    String? captchaKey,
    String? deviceId,
    String? deviceInfo,
  }) async {
    try {
      _setLoading(true);
      _clearError();
      
      final request = LoginRequest(
        identifier: identifier,
        password: password,
        captcha: captcha,
        captchaKey: captchaKey,
        rememberMe: rememberMe,
        deviceId: deviceId,
        deviceInfo: deviceInfo,
      );
      
      final response = await _authRepository.login(request);
      
      if (response.success && response.data != null) {
        _currentUser = response.data!.user;
        _rememberMe = rememberMe;
        _setStatus(AuthStatus.authenticated);
        
        AppLogger.info('AuthProvider: 登录成功', {
          'userId': _currentUser!.id,
          'username': _currentUser!.username,
        });
        
        return true;
      } else {
        _setError(response.message ?? '登录失败');
        _setStatus(AuthStatus.unauthenticated);
        return false;
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 登录失败', e, stackTrace);
      _setError('登录失败: ${e.toString()}');
      _setStatus(AuthStatus.error);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 用户注册
  Future<bool> register(
    String username,
    String email,
    String password, {
    String? confirmPassword,
    String? phone,
    String role = 'student',
    String? realName,
    String? school,
    String? department,
    String? inviteCode,
    String? captcha,
    String? captchaKey,
  }) async {
    try {
      _setLoading(true);
      _clearError();
      
      final request = RegisterRequest(
        username: username,
        email: email,
        password: password,
        confirmPassword: confirmPassword ?? password,
        phone: phone,
        role: role,
        realName: realName,
        school: school,
        department: department,
        inviteCode: inviteCode,
        captcha: captcha,
        captchaKey: captchaKey,
      );
      
      final response = await _authRepository.register(request);
      
      if (response.success && response.data != null) {
        _currentUser = response.data!.user;
        _setStatus(AuthStatus.authenticated);
        
        AppLogger.info('AuthProvider: 注册成功', {
          'userId': _currentUser!.id,
          'username': _currentUser!.username,
        });
        
        return true;
      } else {
        _setError(response.message ?? '注册失败');
        _setStatus(AuthStatus.unauthenticated);
        return false;
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 注册失败', e, stackTrace);
      _setError('注册失败: ${e.toString()}');
      _setStatus(AuthStatus.error);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 用户登出
  Future<void> logout() async {
    try {
      _setLoading(true);
      _clearError();
      
      await _authRepository.logout();
      
      _currentUser = null;
      _rememberMe = false;
      _setStatus(AuthStatus.unauthenticated);
      
      AppLogger.info('AuthProvider: 登出成功');
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 登出失败', e, stackTrace);
      // 即使登出失败，也清除本地状态
      _currentUser = null;
      _rememberMe = false;
      _setStatus(AuthStatus.unauthenticated);
    } finally {
      _setLoading(false);
    }
  }

  /// 更新用户资料
  Future<bool> updateProfile(Map<String, dynamic> userData) async {
    if (!isAuthenticated) return false;
    
    try {
      _setLoading(true);
      _clearError();
      
      final request = ProfileUpdateRequest(
        realName: userData['realName'] ?? userData['real_name'],
        phone: userData['phone'],
        avatar: userData['avatar'],
        school: userData['school'],
        department: userData['department'],
        title: userData['title'],
        profile: userData['profile'] as Map<String, dynamic>?,
      );
      
      final response = await _authRepository.updateProfile(request);
      
      if (response.success && response.data != null) {
        _currentUser = response.data;
        notifyListeners();
        
        AppLogger.info('AuthProvider: 用户资料更新成功');
        return true;
      } else {
        _setError(response.message ?? '更新资料失败');
        return false;
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 用户资料更新失败', e, stackTrace);
      _setError('更新资料失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 修改密码
  Future<bool> changePassword(String oldPassword, String newPassword) async {
    if (!isAuthenticated) return false;
    
    try {
      _setLoading(true);
      _clearError();
      
      final request = PasswordUpdateRequest(
        currentPassword: oldPassword,
        newPassword: newPassword,
        confirmPassword: newPassword,
      );
      
      final response = await _authRepository.updatePassword(request);
      
      if (response.success) {
        AppLogger.info('AuthProvider: 密码更新成功');
        return true;
      } else {
        _setError(response.message ?? '密码更新失败');
        return false;
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 密码更新失败', e, stackTrace);
      _setError('密码更新失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 忘记密码
  Future<bool> forgotPassword(String email) async {
    try {
      _setLoading(true);
      _clearError();
      
      final request = PasswordResetRequest(email: email);
      final response = await _authRepository.sendPasswordResetEmail(request);
      
      if (response.success) {
        AppLogger.info('AuthProvider: 密码重置邮件发送成功');
        return true;
      } else {
        _setError(response.message ?? '发送密码重置邮件失败');
        return false;
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 发送密码重置邮件失败', e, stackTrace);
      _setError('发送密码重置邮件失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 刷新用户信息
  Future<void> refreshUserInfo({bool forceRefresh = false}) async {
    if (!isAuthenticated) return;
    
    try {
      final response = await _authRepository.getCurrentUser(forceRefresh: forceRefresh);
      
      if (response.success && response.data != null) {
        _currentUser = response.data;
        notifyListeners();
        AppLogger.info('AuthProvider: 用户信息刷新成功');
      } else {
        AppLogger.warning('AuthProvider: 用户信息刷新失败', {
          'message': response.message,
        });
      }
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 用户信息刷新异常', e, stackTrace);
    }
  }

  /// 检查用户名可用性
  Future<bool> checkUsernameAvailability(String username) async {
    try {
      final response = await _authRepository.checkUsernameAvailability(username);
      return response.success && (response.data ?? false);
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 检查用户名可用性失败', e, stackTrace);
      return false;
    }
  }

  /// 检查邮箱可用性
  Future<bool> checkEmailAvailability(String email) async {
    try {
      final response = await _authRepository.checkEmailAvailability(email);
      return response.success && (response.data ?? false);
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 检查邮箱可用性失败', e, stackTrace);
      return false;
    }
  }

  /// 获取验证码
  Future<Map<String, dynamic>?> getCaptcha() async {
    try {
      final response = await _authRepository.getCaptcha();
      if (response.success) {
        return response.data;
      }
      return null;
    } catch (e, stackTrace) {
      AppLogger.error('AuthProvider: 获取验证码失败', e, stackTrace);
      return null;
    }
  }

  /// 清除错误信息
  void clearError() {
    _clearError();
  }

  /// 设置记住我状态
  void setRememberMe(bool value) {
    _rememberMe = value;
    notifyListeners();
  }

  // 私有方法

  void _setStatus(AuthStatus status) {
    if (_status != status) {
      _status = status;
      notifyListeners();
    }
  }

  void _setLoading(bool loading) {
    if (_isLoading != loading) {
      _isLoading = loading;
      notifyListeners();
    }
  }

  void _setError(String message) {
    _errorMessage = message;
    notifyListeners();
  }

  void _clearError() {
    if (_errorMessage != null) {
      _errorMessage = null;
      notifyListeners();
    }
  }

  /// 静默刷新用户信息（不显示加载状态）
  void _refreshUserInfo() {
    refreshUserInfo().catchError((e) {
      // 静默处理错误，不影响用户体验
      AppLogger.warning('AuthProvider: 静默刷新用户信息失败', {
        'error': e.toString(),
      });
    });
  }

  @override
  void dispose() {
    super.dispose();
  }
}
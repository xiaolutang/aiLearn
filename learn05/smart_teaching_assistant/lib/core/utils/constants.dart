/// 应用常量配置
class AppConstants {
  // 应用信息
  static const String appName = '智能教学助手';
  static const String appVersion = '1.0.0';
  static const String appDescription = '智能教学助手 - 提供高效成绩录入与分析、班级及年级成绩综合分析、学生个性化成绩分析及练题指导、辅导方案生成等功能';
  
  // 开发者信息
  static const String developerName = '智能教学助手团队';
  static const String developerEmail = 'support@smartteaching.com';
  
  // 应用配置
  static const bool isDebugMode = true; // 生产环境需要设置为false
  static const String defaultLanguage = 'zh_CN';
  static const String defaultTheme = 'light';
}

/// API相关常量
class ApiConstants {
  // 基础配置
  static const String baseUrl = 'http://localhost:8000'; // 本地开发服务器
  static const String apiVersion = 'v1';
  
  // 超时配置
  static const Duration defaultTimeout = Duration(seconds: 30);
  static const Duration uploadTimeout = Duration(minutes: 5);
  static const Duration downloadTimeout = Duration(minutes: 10);
  
  // 调试模式
  static const bool isDebugMode = AppConstants.isDebugMode;
  
  // 认证相关
  static const String tokenKey = 'auth_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'user_data';
  
  // API端点
  static const String authEndpoint = '/auth';
  static const String userEndpoint = '/users';
  static const String gradeEndpoint = '/grades';
  static const String studentEndpoint = '/students';
  static const String classEndpoint = '/classes';
  static const String lessonEndpoint = '/lessons';
  static const String analysisEndpoint = '/analysis';
  
  // 文件上传
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
  static const List<String> allowedImageTypes = ['jpg', 'jpeg', 'png', 'gif'];
  static const List<String> allowedDocumentTypes = ['pdf', 'doc', 'docx', 'xls', 'xlsx'];
}

/// 存储相关常量
class StorageConstants {
  // SharedPreferences键名
  static const String isFirstLaunch = 'is_first_launch';
  static const String userToken = 'user_token';
  static const String refreshToken = 'refresh_token';
  static const String userData = 'user_data';
  static const String themeMode = 'theme_mode';
  static const String languageCode = 'language_code';
  static const String lastSyncTime = 'last_sync_time';
  
  // 本地数据库
  static const String databaseName = 'smart_teaching_assistant.db';
  static const int databaseVersion = 1;
  
  // 缓存配置
  static const Duration cacheExpiration = Duration(hours: 24);
  static const int maxCacheSize = 50 * 1024 * 1024; // 50MB
}

/// UI相关常量
class UIConstants {
  // 间距
  static const double paddingSmall = 8.0;
  static const double paddingMedium = 16.0;
  static const double paddingLarge = 24.0;
  static const double paddingXLarge = 32.0;
  
  // 圆角
  static const double radiusSmall = 4.0;
  static const double radiusMedium = 8.0;
  static const double radiusLarge = 12.0;
  static const double radiusXLarge = 16.0;
  
  // 字体大小
  static const double fontSizeSmall = 12.0;
  static const double fontSizeMedium = 14.0;
  static const double fontSizeLarge = 16.0;
  static const double fontSizeXLarge = 18.0;
  static const double fontSizeXXLarge = 20.0;
  static const double fontSizeTitle = 24.0;
  
  // 图标大小
  static const double iconSizeSmall = 16.0;
  static const double iconSizeMedium = 24.0;
  static const double iconSizeLarge = 32.0;
  static const double iconSizeXLarge = 48.0;
  
  // 按钮高度
  static const double buttonHeightSmall = 32.0;
  static const double buttonHeightMedium = 40.0;
  static const double buttonHeightLarge = 48.0;
  
  // 动画时长
  static const Duration animationDurationFast = Duration(milliseconds: 200);
  static const Duration animationDurationMedium = Duration(milliseconds: 300);
  static const Duration animationDurationSlow = Duration(milliseconds: 500);
  
  // 分页
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
}

/// 业务相关常量
class BusinessConstants {
  // 成绩相关
  static const double maxScore = 100.0;
  static const double minScore = 0.0;
  static const double passingScore = 60.0;
  
  // 等级划分
  static const Map<String, double> gradeThresholds = {
    'A+': 95.0,
    'A': 90.0,
    'B+': 85.0,
    'B': 80.0,
    'C+': 75.0,
    'C': 70.0,
    'D+': 65.0,
    'D': 60.0,
    'F': 0.0,
  };
  
  // 学科列表
  static const List<String> subjects = [
    '语文',
    '数学',
    '英语',
    '物理',
    '化学',
    '生物',
    '政治',
    '历史',
    '地理',
    '体育',
    '音乐',
    '美术',
    '信息技术',
  ];
  
  // 年级列表
  static const List<String> grades = [
    '一年级',
    '二年级',
    '三年级',
    '四年级',
    '五年级',
    '六年级',
    '七年级',
    '八年级',
    '九年级',
    '高一',
    '高二',
    '高三',
  ];
  
  // 班级类型
  static const List<String> classTypes = [
    '普通班',
    '重点班',
    '实验班',
    '特长班',
  ];
}

/// 错误消息常量
class ErrorMessages {
  // 网络错误
  static const String networkError = '网络连接失败，请检查网络设置';
  static const String timeoutError = '请求超时，请稍后重试';
  static const String serverError = '服务器错误，请稍后重试';
  
  // 认证错误
  static const String loginRequired = '请先登录';
  static const String tokenExpired = '登录已过期，请重新登录';
  static const String invalidCredentials = '用户名或密码错误';
  static const String accountDisabled = '账户已被禁用';
  
  // 表单验证错误
  static const String emailRequired = '请输入邮箱地址';
  static const String emailInvalid = '邮箱格式不正确';
  static const String passwordRequired = '请输入密码';
  static const String passwordTooShort = '密码长度至少6位';
  static const String passwordMismatch = '两次输入的密码不一致';
  static const String nameRequired = '请输入姓名';
  static const String phoneRequired = '请输入手机号码';
  static const String phoneInvalid = '手机号码格式不正确';
  
  // 文件错误
  static const String fileNotFound = '文件不存在';
  static const String fileTooLarge = '文件大小超出限制';
  static const String fileTypeNotSupported = '不支持的文件类型';
  static const String uploadFailed = '文件上传失败';
  
  // 数据错误
  static const String dataNotFound = '数据不存在';
  static const String dataInvalid = '数据格式错误';
  static const String saveFailed = '保存失败';
  static const String deleteFailed = '删除失败';
}

/// 成功消息常量
class SuccessMessages {
  static const String loginSuccess = '登录成功';
  static const String registerSuccess = '注册成功';
  static const String logoutSuccess = '登出成功';
  static const String saveSuccess = '保存成功';
  static const String deleteSuccess = '删除成功';
  static const String updateSuccess = '更新成功';
  static const String uploadSuccess = '上传成功';
  static const String passwordChanged = '密码修改成功';
  static const String profileUpdated = '资料更新成功';
}
class AppConstants {
  // 应用信息
  static const String appName = '智能教学助手';
  static const String appVersion = '1.0.0';
  static const String appDescription = '高效成绩录入与分析、班级及年级成绩综合分析、学生个性化成绩分析及练题指导';
  
  // API配置
  static const String baseUrl = 'http://localhost:8000';
  static const String apiVersion = 'v1';
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  
  // API端点
  static const String loginEndpoint = '/api/v1/auth/login';
  static const String registerEndpoint = '/api/v1/auth/register';
  static const String refreshTokenEndpoint = '/api/v1/auth/refresh';
  static const String logoutEndpoint = '/api/v1/auth/logout';
  
  static const String gradesEndpoint = '/api/v1/grades';
  static const String studentsEndpoint = '/api/v1/students';
  static const String classesEndpoint = '/api/v1/classes';
  static const String lessonsEndpoint = '/api/v1/lessons';
  static const String teachingEndpoint = '/api/v1/teaching';
  static const String analysisEndpoint = '/api/v1/analysis';
  
  // 存储键
  static const String tokenKey = 'auth_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userInfoKey = 'user_info';
  static const String themeKey = 'theme_mode';
  static const String languageKey = 'language';
  
  // 分页配置
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
  
  // 文件配置
  static const List<String> supportedImageFormats = ['jpg', 'jpeg', 'png', 'gif'];
  static const List<String> supportedDocumentFormats = ['pdf', 'doc', 'docx', 'xls', 'xlsx'];
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
  
  // 成绩配置
  static const double maxScore = 100.0;
  static const double minScore = 0.0;
  static const List<String> gradeTypes = ['期中考试', '期末考试', '月考', '周测', '作业'];
  static const List<String> subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治'];
  
  // 班级配置
  static const int maxStudentsPerClass = 60;
  static const int minStudentsPerClass = 1;
  
  // 缓存配置
  static const Duration cacheExpiration = Duration(hours: 24);
  static const int maxCacheSize = 100;
  
  // 动画配置
  static const Duration animationDuration = Duration(milliseconds: 300);
  static const Duration shortAnimationDuration = Duration(milliseconds: 150);
  static const Duration longAnimationDuration = Duration(milliseconds: 500);
  
  // 错误消息
  static const String networkErrorMessage = '网络连接失败，请检查网络设置';
  static const String serverErrorMessage = '服务器错误，请稍后重试';
  static const String unknownErrorMessage = '未知错误，请联系技术支持';
  static const String timeoutErrorMessage = '请求超时，请稍后重试';
  static const String authErrorMessage = '认证失败，请重新登录';
  
  // 成功消息
  static const String loginSuccessMessage = '登录成功';
  static const String logoutSuccessMessage = '退出成功';
  static const String saveSuccessMessage = '保存成功';
  static const String deleteSuccessMessage = '删除成功';
  static const String updateSuccessMessage = '更新成功';
  
  // 正则表达式
  static const String emailRegex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
  static const String phoneRegex = r'^1[3-9]\d{9}$';
  static const String passwordRegex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$';
  
  // 数据库配置
  static const String databaseName = 'smart_teaching_assistant.db';
  static const int databaseVersion = 1;
  
  // 图表配置
  static const List<String> chartColors = [
    '#2E7D32', // 主绿色
    '#4CAF50', // 绿色
    '#81C784', // 浅绿色
    '#2196F3', // 蓝色
    '#FF9800', // 橙色
    '#F44336', // 红色
    '#9C27B0', // 紫色
    '#607D8B', // 蓝灰色
  ];
  
  // 导出配置
  static const List<String> exportFormats = ['PDF', 'Excel', 'Word'];
  
  // 权限配置
  static const List<String> requiredPermissions = [
    'camera',
    'storage',
    'microphone',
  ];
}
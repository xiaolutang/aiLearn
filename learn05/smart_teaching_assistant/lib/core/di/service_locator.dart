import 'package:get_it/get_it.dart';

import '../data/repositories/auth_repository.dart';
import '../data/repositories/class_repository.dart';
import '../data/repositories/grade_repository.dart';
import '../data/repositories/student_repository.dart';
import '../data/repositories/subject_repository.dart';
import '../data/repositories/tutoring_repository.dart';
import '../data/datasources/local_data_source.dart';
import '../data/datasources/remote_data_source.dart';
import '../services/connectivity_service.dart';
import '../utils/api_client.dart';
import '../services/offline_manager.dart';

/// 服务定位器
/// 负责管理依赖注入和服务实例化
class ServiceLocator {
  static final GetIt _getIt = GetIt.instance;
  
  /// 获取GetIt实例
  static GetIt get instance => _getIt;
  
  /// 初始化所有依赖
  static Future<void> init() async {
    // 注册核心服务
    await _registerCoreServices();
    
    // 注册数据源
    await _registerDataSources();
    
    // 注册Repository
    await _registerRepositories();
  }
  
  /// 注册核心服务
  static Future<void> _registerCoreServices() async {
    // API客户端
    _getIt.registerLazySingleton<ApiClient>(
      () {
        final client = ApiClient();
        client.initialize();
        return client;
      },
    );
    
    // 连接服务
    _getIt.registerLazySingleton<ConnectivityService>(
      () => ConnectivityService.instance..init(),
    );
    
    // 离线管理器
    _getIt.registerLazySingleton<OfflineManager>(
      () => OfflineManager.instance,
    );
  }
  
  /// 注册数据源
  static Future<void> _registerDataSources() async {
    // 远程数据源
    _getIt.registerLazySingleton<RemoteDataSource>(
      () {
        final dataSource = RemoteDataSourceImpl();
        dataSource.initialize();
        return dataSource;
      },
    );
    
    // 本地数据源
    _getIt.registerLazySingleton<LocalDataSource>(
      () {
        final dataSource = LocalDataSourceImpl();
        dataSource.initialize();
        return dataSource;
      },
    );
  }
  
  /// 注册Repository
  static Future<void> _registerRepositories() async {
    // 认证Repository
    _getIt.registerLazySingleton<AuthRepository>(
      () => AuthRepositoryImpl(
        remoteDataSource: _getIt<RemoteDataSource>(),
        localDataSource: _getIt<LocalDataSource>(),
        connectivityService: _getIt<ConnectivityService>(),
      ),
    );
    
    // 班级Repository
    _getIt.registerLazySingleton<ClassRepository>(
      () => ClassRepositoryImpl(
        remoteDataSource: _getIt<RemoteDataSource>(),
        localDataSource: _getIt<LocalDataSource>(),
        connectivityService: _getIt<ConnectivityService>(),
      ),
    );
    
    // 成绩Repository
    _getIt.registerLazySingleton<GradeRepository>(
      () => GradeRepositoryImpl(
        remoteDataSource: _getIt<RemoteDataSource>(),
        localDataSource: _getIt<LocalDataSource>(),
        connectivityService: _getIt<ConnectivityService>(),
      ),
    );
    
    // 学生Repository
    _getIt.registerLazySingleton<StudentRepository>(
      () => StudentRepositoryImpl(
        remoteDataSource: _getIt<RemoteDataSource>(),
        localDataSource: _getIt<LocalDataSource>(),
        connectivityService: _getIt<ConnectivityService>(),
      ),
    );
    
    // 学科Repository
    _getIt.registerLazySingleton<SubjectRepository>(
      () => SubjectRepositoryImpl(
        remoteDataSource: _getIt<RemoteDataSource>(),
        localDataSource: _getIt<LocalDataSource>(),
        connectivityService: _getIt<ConnectivityService>(),
      ),
    );
    
    // AI辅导Repository
    _getIt.registerLazySingleton<TutoringRepository>(
      () => TutoringRepositoryImpl(
        remoteDataSource: _getIt<RemoteDataSource>(),
        localDataSource: _getIt<LocalDataSource>(),
        connectivityService: _getIt<ConnectivityService>(),
      ),
    );
  }
  
  /// 清理所有注册的服务
  static Future<void> reset() async {
    await _getIt.reset();
  }
  
  /// 获取服务实例的便捷方法
  static T get<T extends Object>() {
    return _getIt.get<T>();
  }
  
  /// 检查服务是否已注册
  static bool isRegistered<T extends Object>() {
    return _getIt.isRegistered<T>();
  }
}
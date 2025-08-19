import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers.dart';
import '../data/repositories/auth_repository.dart';
import '../data/repositories/class_repository.dart';
import '../data/repositories/grade_repository.dart';
import '../data/repositories/student_repository.dart';
import '../data/repositories/subject_repository.dart';
import '../data/repositories/tutoring_repository.dart';
import '../services/connectivity_service.dart';

/// Provider配置类
/// 负责配置和初始化所有的Provider
class ProviderConfig {

  /// 配置所有Provider
  static List<ChangeNotifierProvider> configureProviders({
    required AuthRepository authRepository,
    required ClassRepository classRepository,
    required GradeRepository gradeRepository,
    required StudentRepository studentRepository,
    required SubjectRepository subjectRepository,
    required TutoringRepository tutoringRepository,
    required ConnectivityService connectivityService,
  }) {
    return [
      // 认证Provider
      ChangeNotifierProvider<AuthProvider>(
        create: (context) => AuthProvider(
          authRepository: authRepository,
        ),
      ),
      
      // 班级Provider
      ChangeNotifierProvider<ClassProvider>(
        create: (context) => ClassProvider(
          classRepository: classRepository,
          connectivityService: connectivityService,
        ),
      ),
      
      // 成绩Provider
      ChangeNotifierProvider<GradeProvider>(
        create: (context) => GradeProvider(
          gradeRepository: gradeRepository,
          connectivityService: connectivityService,
        ),
      ),
      
      // 学生Provider
      ChangeNotifierProvider<StudentProvider>(
        create: (context) => StudentProvider(
          studentRepository: studentRepository,
          connectivityService: connectivityService,
        ),
      ),
      
      // 学科Provider
      ChangeNotifierProvider<SubjectProvider>(
        create: (context) => SubjectProvider(
          subjectRepository: subjectRepository,
          connectivityService: connectivityService,
        ),
      ),
      
      // AI辅导Provider
      ChangeNotifierProvider<TutoringProvider>(
        create: (context) => TutoringProvider(
          tutoringRepository: tutoringRepository,
          connectivityService: connectivityService,
        ),
      ),
    ];
  }

  /// 配置ProxyProvider（用于依赖其他Provider的Provider）
  static List<ProxyProvider> configureProxyProviders() {
    return [
      // 示例：如果有Provider需要依赖其他Provider，可以在这里配置
      // ProxyProvider<AuthProvider, SomeOtherProvider>(
      //   update: (context, authProvider, previous) => SomeOtherProvider(
      //     authProvider: authProvider,
      //   ),
      // ),
    ];
  }

  /// 初始化所有Provider
  static Future<void> initializeProviders(BuildContext context) async {
    // 初始化认证状态
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    await authProvider.initialize();
    
    // 如果用户已登录，初始化其他数据
    if (authProvider.isAuthenticated) {
      // 初始化班级数据
      final classProvider = Provider.of<ClassProvider>(context, listen: false);
      classProvider.loadClasses();
      
      // 初始化学科数据
      final subjectProvider = Provider.of<SubjectProvider>(context, listen: false);
      subjectProvider.loadSubjects();
      
      // 初始化学生数据
      final studentProvider = Provider.of<StudentProvider>(context, listen: false);
      studentProvider.loadStudents();
      
      // 初始化成绩数据
      final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
      gradeProvider.loadGrades();
    }
  }

  /// 清理所有Provider状态
  static void clearAllProviders(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final classProvider = Provider.of<ClassProvider>(context, listen: false);
    final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
    final studentProvider = Provider.of<StudentProvider>(context, listen: false);
    final subjectProvider = Provider.of<SubjectProvider>(context, listen: false);
    final tutoringProvider = Provider.of<TutoringProvider>(context, listen: false);
    
    // 重置所有Provider状态
    // 注意：这些Provider可能没有reset方法，需要根据实际情况调整
    // classProvider.reset();
    // gradeProvider.reset();
    // studentProvider.reset();
    // subjectProvider.reset();
    // tutoringProvider.reset();
    
    // 认证Provider最后重置
    authProvider.clearError();
  }

  /// 刷新所有数据
  static Future<void> refreshAllData(BuildContext context) async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    
    if (!authProvider.isAuthenticated) return;
    
    final classProvider = Provider.of<ClassProvider>(context, listen: false);
    final gradeProvider = Provider.of<GradeProvider>(context, listen: false);
    final studentProvider = Provider.of<StudentProvider>(context, listen: false);
    final subjectProvider = Provider.of<SubjectProvider>(context, listen: false);
    
    // 并行刷新所有数据
    await Future.wait([
      classProvider.refresh(),
      gradeProvider.refresh(),
      studentProvider.refresh(),
      subjectProvider.refresh(),
      authProvider.refreshUserInfo(forceRefresh: true),
    ]);
  }

  /// 获取Provider的便捷方法
  static T getProvider<T extends ChangeNotifier>(BuildContext context, {bool listen = false}) {
    return Provider.of<T>(context, listen: listen);
  }

  /// 监听Provider变化的便捷方法
  static Widget consumer<T extends ChangeNotifier>(
    Widget Function(BuildContext context, T provider, Widget? child) builder, {
    Widget? child,
  }) {
    return Consumer<T>(
      builder: builder,
      child: child,
    );
  }

  /// 多Provider监听的便捷方法
  static Widget consumer2<A extends ChangeNotifier, B extends ChangeNotifier>(
    Widget Function(BuildContext context, A providerA, B providerB, Widget? child) builder, {
    Widget? child,
  }) {
    return Consumer2<A, B>(
      builder: builder,
      child: child,
    );
  }

  /// 三Provider监听的便捷方法
  static Widget consumer3<A extends ChangeNotifier, B extends ChangeNotifier, C extends ChangeNotifier>(
    Widget Function(BuildContext context, A providerA, B providerB, C providerC, Widget? child) builder, {
    Widget? child,
  }) {
    return Consumer3<A, B, C>(
      builder: builder,
      child: child,
    );
  }

  /// Selector的便捷方法
  static Widget selector<T extends ChangeNotifier, S>(
    S Function(BuildContext context, T provider) selector,
    Widget Function(BuildContext context, S value, Widget? child) builder, {
    Widget? child,
    bool Function(S previous, S next)? shouldRebuild,
  }) {
    return Selector<T, S>(
      selector: selector,
      builder: builder,
      child: child,
      shouldRebuild: shouldRebuild,
    );
  }
}

/// Provider扩展方法
extension ProviderExtension on BuildContext {
  /// 获取Provider（不监听）
  T read<T extends ChangeNotifier>() {
    return Provider.of<T>(this, listen: false);
  }

  /// 获取Provider（监听）
  T watch<T extends ChangeNotifier>() {
    return Provider.of<T>(this, listen: true);
  }

  /// 选择性监听Provider的某个属性
  S select<T extends ChangeNotifier, S>(S Function(T provider) selector) {
    return selector(Provider.of<T>(this));
  }
}
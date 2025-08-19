import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'routes/app_router.dart';
import 'shared/themes/app_theme.dart';
import 'core/providers/provider_config.dart';
import 'core/di/service_locator.dart';
import 'core/services/offline_manager.dart';
import 'core/utils/app_logger.dart';

void main() async {
  // 确保Flutter绑定初始化
  WidgetsFlutterBinding.ensureInitialized();
  
  // 设置系统UI样式
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );
  
  try {
    // 初始化依赖注入
    await ServiceLocator.init();
    AppLogger.info('Service locator initialized successfully');
    
    // 初始化离线管理器
    await OfflineManager.instance.init();
    AppLogger.info('Application initialized successfully');
  } catch (e, stackTrace) {
    AppLogger.error('Failed to initialize application', e, stackTrace);
    // 即使初始化失败，也要启动应用，但会在离线模式下运行
  }
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ScreenUtilInit(
      designSize: const Size(375, 812), // iPhone X 设计尺寸
      minTextAdapt: true,
      splitScreenMode: true,
      builder: (context, child) {
        return MultiProvider(
          providers: ProviderConfig.configureProviders(
            authRepository: ServiceLocator.get(),
            classRepository: ServiceLocator.get(),
            gradeRepository: ServiceLocator.get(),
            studentRepository: ServiceLocator.get(),
            subjectRepository: ServiceLocator.get(),
            tutoringRepository: ServiceLocator.get(),
            connectivityService: ServiceLocator.get(),
          ),
          child: MaterialApp.router(
            title: '智能教学助手',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: ThemeMode.system,
            routerConfig: AppRouter.router,
            builder: (context, widget) {
              return MediaQuery(
                data: MediaQuery.of(context).copyWith(textScaleFactor: 1.0),
                child: widget!,
              );
            },
          ),
        );
      },
    );
  }
}

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../features/auth/presentation/pages/login_page.dart';
import '../features/auth/presentation/pages/register_page.dart';
import '../features/auth/presentation/pages/forgot_password_page.dart';
import '../features/auth/presentation/pages/profile_page.dart' as auth;
import '../features/home/presentation/pages/home_page.dart';
import '../features/grades/presentation/pages/grades_page.dart';
import '../features/grades/presentation/pages/grade_input_page.dart';
import '../features/grades/presentation/pages/grade_analysis_page.dart';
import '../features/analytics/presentation/pages/analytics_page.dart';
import '../features/students/presentation/pages/students_page.dart';
import '../features/students/presentation/pages/student_detail_page.dart';
import '../features/classes/presentation/pages/classes_page.dart';
import '../features/classes/presentation/pages/class_detail_page.dart';
import '../features/lessons/presentation/pages/lessons_page.dart';
import '../features/lessons/presentation/pages/lesson_detail_page.dart';
import '../features/lessons/presentation/pages/create_lesson_page.dart';
import '../features/teaching/presentation/pages/teaching_page.dart';
import '../pages/profile_page.dart' as profile_center;

class AppRouter {
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String forgotPassword = '/forgot-password';
  static const String profile = '/profile';
  static const String home = '/home';
  static const String grades = '/grades';
  static const String gradeInput = '/grades/input';
  static const String gradeAnalysis = '/grades/analysis';
  static const String analytics = '/analytics';
  static const String students = '/students';
  static const String studentDetail = '/students/:id';
  static const String classes = '/classes';
  static const String classDetail = '/classes/:id';
  static const String lessons = '/lessons';
  static const String lessonDetail = '/lessons/:id';
  static const String createLesson = '/lessons/create';
  static const String teaching = '/teaching';
  static const String profileCenter = '/profile-center';
  
  static final GoRouter router = GoRouter(
    initialLocation: splash,
    routes: [
      // 启动页
      GoRoute(
        path: splash,
        name: 'splash',
        builder: (context, state) => const SplashPage(),
      ),
      
      // 认证相关路由
      GoRoute(
        path: login,
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: register,
        name: 'register',
        builder: (context, state) => const RegisterPage(),
      ),
      GoRoute(
        path: forgotPassword,
        name: 'forgotPassword',
        builder: (context, state) => const ForgotPasswordPage(),
      ),
      GoRoute(
        path: profile,
        name: 'profile',
        builder: (context, state) => const auth.ProfilePage(),
      ),
      
      // 主页
      GoRoute(
        path: home,
        name: 'home',
        builder: (context, state) => const HomePage(),
      ),
      
      // 成绩管理路由
      GoRoute(
        path: grades,
        name: 'grades',
        builder: (context, state) => const GradesPage(),
        routes: [
          GoRoute(
            path: 'input',
            name: 'gradeInput',
            builder: (context, state) => const GradeInputPage(),
          ),
          GoRoute(
            path: 'analysis',
            name: 'gradeAnalysis',
            builder: (context, state) => const GradeAnalysisPage(),
          ),
        ],
      ),
      
      // 学生管理路由
      GoRoute(
        path: students,
        name: 'students',
        builder: (context, state) => const StudentsPage(),
        routes: [
          GoRoute(
            path: ':id',
            name: 'studentDetail',
            builder: (context, state) {
              final id = state.params['id']!;
              return StudentDetailPage(studentId: id);
            },
          ),
        ],
      ),
      
      // 班级管理路由
      GoRoute(
        path: classes,
        name: 'classes',
        builder: (context, state) => const ClassesPage(),
        routes: [
          GoRoute(
            path: ':id',
            name: 'classDetail',
            builder: (context, state) {
              final id = state.params['id']!;
              return ClassDetailPage(classId: id);
            },
          ),
        ],
      ),
      
      // 备课管理路由
      GoRoute(
        path: lessons,
        name: 'lessons',
        builder: (context, state) => const LessonsPage(),
        routes: [
          GoRoute(
            path: 'create',
            name: 'createLesson',
            builder: (context, state) => const CreateLessonPage(),
          ),
          GoRoute(
            path: ':id',
            name: 'lessonDetail',
            builder: (context, state) {
              final id = state.params['id']!;
              return LessonDetailPage(lessonId: id);
            },
          ),
        ],
      ),
      
      // 上课管理路由
      GoRoute(
        path: teaching,
        name: 'teaching',
        builder: (context, state) => const TeachingPage(),
      ),
      
      // 学情分析路由
      GoRoute(
        path: analytics,
        name: 'analytics',
        builder: (context, state) => const AnalyticsPage(),
      ),
      
      // 个人中心路由
      GoRoute(
        path: profileCenter,
        name: 'profileCenter',
        builder: (context, state) => const profile_center.ProfilePage(),
      ),
    ],
    
    // 错误页面
    errorBuilder: (context, state) => Scaffold(
      appBar: AppBar(
        title: const Text('页面未找到'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              '页面未找到: ${state.location}',
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => context.go(home),
              child: const Text('返回首页'),
            ),
          ],
        ),
      ),
    ),
    
    // 路由重定向
    redirect: (context, state) {
      // 这里可以添加认证检查逻辑
      // 例如：如果用户未登录且不在登录页面，则重定向到登录页
      return null;
    },
  );
}

// 启动页
class SplashPage extends StatefulWidget {
  const SplashPage({super.key});

  @override
  State<SplashPage> createState() => _SplashPageState();
}

class _SplashPageState extends State<SplashPage> {
  @override
  void initState() {
    super.initState();
    _navigateToHome();
  }

  _navigateToHome() async {
    await Future.delayed(const Duration(seconds: 2));
    if (mounted) {
      context.go(AppRouter.login);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF2E7D32),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: const Icon(
                Icons.school,
                size: 60,
                color: Color(0xFF2E7D32),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              '智能教学助手',
              style: TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              '高效成绩录入与分析',
              style: TextStyle(
                color: Colors.white70,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 48),
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            ),
          ],
        ),
      ),
    );
  }
}
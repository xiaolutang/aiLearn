import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:form_field_validator/form_field_validator.dart';
import '../../../../routes/app_router.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/utils/constants.dart';
import '../../../../core/utils/app_logger.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isPasswordVisible = false;
  bool _rememberMe = false;

  @override
  void initState() {
    super.initState();
    AppLogger.info('LoginPage: 页面初始化');
  }

  @override
  void dispose() {
    AppLogger.debug('LoginPage: 页面销毁，清理资源');
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    AppLogger.info('LoginPage: 用户点击登录按钮');
    
    if (!_formKey.currentState!.validate()) {
      AppLogger.warning('LoginPage: 表单验证失败');
      return;
    }

    final username = _usernameController.text.trim();
    AppLogger.debug('LoginPage: 表单验证通过，开始登录流程', {'username': username, 'rememberMe': _rememberMe});

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    
    try {
      final success = await authProvider.login(username, _passwordController.text, rememberMe: _rememberMe);

      if (success && mounted) {
        AppLogger.info('LoginPage: 登录成功，导航到主页', {'username': username});
        context.go(AppRouter.home);
      } else if (mounted) {
        final errorMessage = authProvider.errorMessage ?? '登录失败';
        AppLogger.warning('LoginPage: 登录失败', {'username': username, 'error': errorMessage});
        _showErrorSnackBar(errorMessage);
      }
    } catch (e, stackTrace) {
      AppLogger.error('LoginPage: 登录过程中发生异常', e, stackTrace);
      if (mounted) {
        _showErrorSnackBar('登录过程中发生错误');
      }
    }
  }

  /// 显示错误提示
  void _showErrorSnackBar(String message) {
    AppLogger.debug('LoginPage: 显示错误提示', {'message': message});
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
        margin: EdgeInsets.all(UIConstants.paddingMedium.w),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(UIConstants.radiusMedium.r),
        ),
      ),
    );
  }

  /// 导航到注册页面
  void _navigateToRegister() {
    AppLogger.info('LoginPage: 用户点击注册链接，导航到注册页面');
    context.push('/register');
  }

  /// 忘记密码
  void _forgotPassword() {
    AppLogger.info('LoginPage: 用户点击忘记密码');
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('忘记密码功能即将上线'),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: LayoutBuilder(
        builder: (context, constraints) {
          if (constraints.maxWidth > 768) {
            return _buildDesktopLayout();
          } else {
            return _buildMobileLayout();
          }
        },
      ),
    );
  }

  Widget _buildDesktopLayout() {
    return Row(
      children: [
        // 左侧品牌区域
        Expanded(
          flex: 5,
          child: Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFF667EEA),
                  Color(0xFF764BA2),
                ],
              ),
            ),
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(60),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildBrandLogo(),
                    const SizedBox(height: 60),
                    Expanded(
                      child: SingleChildScrollView(
                        child: _buildFeatureHighlights(),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        // 右侧登录表单区域
        Expanded(
          flex: 4,
          child: Container(
            color: Colors.white,
            child: SafeArea(
              child: Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(60),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 400),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _buildFormHeader(),
                        const SizedBox(height: 40),
                        _buildLoginForm(),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMobileLayout() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0xFF667EEA),
            Color(0xFF764BA2),
          ],
        ),
      ),
      child: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const SizedBox(height: 40),
              _buildBrandLogo(),
              const SizedBox(height: 60),
              Container(
                padding: const EdgeInsets.all(32),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _buildFormHeader(),
                    const SizedBox(height: 32),
                    _buildLoginForm(),
                  ],
                ),
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBrandLogo() {
    return Column(
      children: [
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Icon(
            Icons.school,
            size: 36,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 20),
        const Text(
          '智能教学助手',
          style: TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.w600,
            color: Colors.white,
            letterSpacing: 1,
          ),
        ),
        const SizedBox(height: 12),
        Text(
          '让教学更智能，让学习更高效',
          style: TextStyle(
            fontSize: 16,
            color: Colors.white.withOpacity(0.9),
            height: 1.5,
          ),
        ),
      ],
    );
  }

  Widget _buildFeatureHighlights() {
    final features = [
      {'icon': '🤖', 'title': 'AI智能分析', 'desc': '智能分析学情，个性化教学建议'},
      {'icon': '📊', 'title': '数据可视化', 'desc': '直观展示成绩趋势和学习进度'},
      {'icon': '📱', 'title': '多端同步', 'desc': '支持PC、平板、手机多端使用'},
    ];

    return Column(
      children: features.map((feature) => _buildFeatureItem(feature)).toList(),
    );
  }

  Widget _buildFeatureItem(Map<String, String> feature) {
    return Container(
      margin: const EdgeInsets.only(bottom: 24),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Center(
              child: Text(
                feature['icon']!,
                style: const TextStyle(fontSize: 18),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  feature['title']!,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  feature['desc']!,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.white.withOpacity(0.8),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFormHeader() {
    return Column(
      children: [
        const Text(
          '欢迎回来',
          style: TextStyle(
            fontSize: 28,
            color: Color(0xFF262626),
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          '请登录您的账户继续使用',
          style: TextStyle(
            fontSize: 16,
            color: Color(0xFF8C8C8C),
          ),
        ),
      ],
    );
  }

  Widget _buildLoginForm() {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          _buildFormGroup(
            label: '用户名/手机号',
            child: TextFormField(
              controller: _usernameController,
              decoration: _buildInputDecoration('请输入用户名或手机号'),
              validator: MultiValidator([
                RequiredValidator(errorText: '用户名不能为空'),
                MinLengthValidator(3, errorText: '用户名至少3个字符'),
              ]),
            ),
          ),
          SizedBox(height: 24.h),
          _buildFormGroup(
            label: '密码',
            child: TextFormField(
              controller: _passwordController,
              obscureText: !_isPasswordVisible,
              decoration: _buildInputDecoration(
                '请输入密码',
                suffixIcon: IconButton(
                  icon: Icon(
                    _isPasswordVisible
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                    color: const Color(0xFF8C8C8C),
                  ),
                  onPressed: () {
                    AppLogger.debug('LoginPage: 用户切换密码可见性', {'visible': !_isPasswordVisible});
                    setState(() {
                      _isPasswordVisible = !_isPasswordVisible;
                    });
                  },
                ),
              ),
              validator: MultiValidator([
                RequiredValidator(errorText: ErrorMessages.passwordRequired),
                MinLengthValidator(6, errorText: ErrorMessages.passwordTooShort),
              ]),
            ),
          ),
          SizedBox(height: 24.h),
          _buildFormOptions(),
          SizedBox(height: 32.h),
          _buildLoginButton(),
          SizedBox(height: 24.h),
          _buildDivider(),
          SizedBox(height: 24.h),
          _buildSocialLogin(),
          SizedBox(height: 24.h),
          _buildRegisterLink(),
        ],
      ),
    );
  }

  Widget _buildFormGroup({required String label, required Widget child}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 14.sp,
            fontWeight: FontWeight.w500,
            color: const Color(0xFF262626),
          ),
        ),
        SizedBox(height: 8.h),
        child,
      ],
    );
  }

  InputDecoration _buildInputDecoration(String hintText, {Widget? suffixIcon}) {
    return InputDecoration(
      hintText: hintText,
      hintStyle: TextStyle(
        color: const Color(0xFFBFBFBF),
        fontSize: 16.sp,
      ),
      suffixIcon: suffixIcon,
      filled: true,
      fillColor: const Color(0xFFFAFAFA),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8.r),
        borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8.r),
        borderSide: const BorderSide(color: Color(0xFFD9D9D9)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8.r),
        borderSide: const BorderSide(color: Color(0xFF1890FF), width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8.r),
        borderSide: const BorderSide(color: Colors.red),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8.r),
        borderSide: const BorderSide(color: Colors.red, width: 2),
      ),
      contentPadding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
    );
  }

  Widget _buildFormOptions() {
    return Row(
      children: [
        Row(
          children: [
            Checkbox(
              value: _rememberMe,
              onChanged: (value) {
                final newValue = value ?? false;
                AppLogger.debug('LoginPage: 用户切换记住我选项', {'rememberMe': newValue});
                setState(() {
                  _rememberMe = newValue;
                });
              },
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              activeColor: const Color(0xFF1890FF),
            ),
            Text(
              '记住我',
              style: TextStyle(
                fontSize: 14.sp,
                color: const Color(0xFF595959),
              ),
            ),
          ],
        ),
        const Spacer(),
        TextButton(
          onPressed: _forgotPassword,
          child: Text(
            '忘记密码？',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF1890FF),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLoginButton() {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        return SizedBox(
          width: double.infinity,
          height: 48.h,
          child: ElevatedButton(
            onPressed: authProvider.isLoading ? null : _handleLogin,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1890FF),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8.r),
              ),
              elevation: 0,
            ).copyWith(
              backgroundColor: MaterialStateProperty.resolveWith<Color>(
                (Set<MaterialState> states) {
                  if (states.contains(MaterialState.hovered)) {
                    return const Color(0xFF096DD9);
                  }
                  return const Color(0xFF1890FF);
                },
              ),
            ),
            child: authProvider.isLoading
                ? SizedBox(
                    width: 20.w,
                    height: 20.w,
                    child: const CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                    ),
                  )
                : Text(
                    '登录',
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
          ),
        );
      },
    );
  }

  Widget _buildDivider() {
    return Row(
      children: [
        const Expanded(
          child: Divider(color: Color(0xFFF0F0F0)),
        ),
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 16.w),
          child: Text(
            '或',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF8C8C8C),
            ),
          ),
        ),
        const Expanded(
          child: Divider(color: Color(0xFFF0F0F0)),
        ),
      ],
    );
  }

  Widget _buildSocialLogin() {
    return Row(
      children: [
        Expanded(
          child: _buildSocialButton('微信登录'),
        ),
        SizedBox(width: 12.w),
        Expanded(
          child: _buildSocialButton('验证码登录'),
        ),
      ],
    );
  }

  Widget _buildSocialButton(String text) {
    return SizedBox(
      height: 48.h,
      child: OutlinedButton(
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('$text功能即将上线'),
              behavior: SnackBarBehavior.floating,
            ),
          );
        },
        style: OutlinedButton.styleFrom(
          side: const BorderSide(color: Color(0xFFD9D9D9)),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8.r),
          ),
        ).copyWith(
          side: MaterialStateProperty.resolveWith<BorderSide>(
            (Set<MaterialState> states) {
              if (states.contains(MaterialState.hovered)) {
                return const BorderSide(color: Color(0xFF1890FF));
              }
              return const BorderSide(color: Color(0xFFD9D9D9));
            },
          ),
          foregroundColor: MaterialStateProperty.resolveWith<Color>(
            (Set<MaterialState> states) {
              if (states.contains(MaterialState.hovered)) {
                return const Color(0xFF1890FF);
              }
              return const Color(0xFF595959);
            },
          ),
        ),
        child: Text(
          text,
          style: TextStyle(
            fontSize: 14.sp,
          ),
        ),
      ),
    );
  }

  Widget _buildRegisterLink() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          '还没有账户？',
          style: TextStyle(
            fontSize: 14.sp,
            color: const Color(0xFF8C8C8C),
          ),
        ),
        TextButton(
          onPressed: _navigateToRegister,
          child: Text(
            '立即注册',
            style: TextStyle(
              fontSize: 14.sp,
              color: const Color(0xFF1890FF),
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }
}
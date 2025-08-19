import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:form_field_validator/form_field_validator.dart';
import '../../../../shared/themes/app_theme.dart';
import '../../../../routes/app_router.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/utils/constants.dart';
import '../../../../core/utils/app_logger.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _isPasswordVisible = false;
  bool _isConfirmPasswordVisible = false;
  bool _agreeToTerms = false;
  String _selectedRole = '教师';

  final List<String> _roles = ['教师', '管理员', '学生'];

  @override
  void initState() {
    super.initState();
    AppLogger.info('RegisterPage: 页面初始化');
  }

  @override
  void dispose() {
    AppLogger.debug('RegisterPage: 页面销毁，清理资源');
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    AppLogger.info('RegisterPage: 用户点击注册按钮');
    
    if (!_formKey.currentState!.validate()) {
      AppLogger.warning('RegisterPage: 表单验证失败');
      return;
    }

    if (!_agreeToTerms) {
      AppLogger.warning('RegisterPage: 用户未同意用户协议');
      _showErrorSnackBar('请同意用户协议和隐私政策');
      return;
    }

    final name = _nameController.text.trim();
    final email = _emailController.text.trim();
    final phone = _phoneController.text.trim();
    
    AppLogger.debug('RegisterPage: 表单验证通过，开始注册流程', {
      'name': name,
      'email': email,
      'phone': phone,
      'role': _selectedRole,
      'agreeToTerms': _agreeToTerms
    });

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    
    try {
      final success = await authProvider.register(name, email, _passwordController.text);

      if (success && mounted) {
        AppLogger.info('RegisterPage: 注册成功，导航到主页', {'email': email, 'name': name});
        context.go(AppRouter.home);
      } else if (mounted) {
        final errorMessage = authProvider.errorMessage ?? '注册失败';
        AppLogger.warning('RegisterPage: 注册失败', {'email': email, 'error': errorMessage});
        _showErrorSnackBar(errorMessage);
      }
    } catch (e, stackTrace) {
      AppLogger.error('RegisterPage: 注册过程中发生异常', e, stackTrace);
      if (mounted) {
        _showErrorSnackBar('注册过程中发生错误');
      }
    }
  }

  /// 显示错误提示
  void _showErrorSnackBar(String message) {
    AppLogger.debug('RegisterPage: 显示错误提示', {'message': message});
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

  /// 导航到登录页面
  void _navigateToLogin() {
    AppLogger.info('RegisterPage: 用户返回登录页面');
    context.pop();
  }

  /// 显示用户协议
  void _showTermsDialog() {
    AppLogger.info('RegisterPage: 用户查看用户协议');
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('用户协议和隐私政策'),
        content: const SingleChildScrollView(
          child: Text(
            '这里是用户协议和隐私政策的内容...\n\n'
            '1. 用户注册即表示同意本协议\n'
            '2. 我们将保护您的个人隐私\n'
            '3. 请合理使用本应用功能\n'
            '4. 如有问题请联系客服',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              AppLogger.debug('RegisterPage: 用户关闭用户协议对话框');
              Navigator.of(context).pop();
            },
            child: const Text('关闭'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios),
          onPressed: _navigateToLogin,
        ),
        title: const Text('注册账户'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(24.w),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(height: 20.h),
                
                // 头部信息
                _buildHeader(),
                
                SizedBox(height: 40.h),
                
                // 注册表单
                _buildRegisterForm(),
                
                SizedBox(height: 16.h),
                
                // 用户协议
                _buildTermsAgreement(),
                
                SizedBox(height: 32.h),
                
                // 注册按钮
                _buildRegisterButton(),
                
                SizedBox(height: 24.h),
                
                // 登录链接
                _buildLoginLink(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// 构建头部
  Widget _buildHeader() {
    return Column(
      children: [
        Text(
          '创建新账户',
          style: TextStyle(
            fontSize: 28.sp,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        SizedBox(height: 8.h),
        Text(
          '请填写以下信息完成注册',
          style: TextStyle(
            fontSize: 16.sp,
            color: AppTheme.textSecondaryColor,
          ),
        ),
      ],
    );
  }

  /// 构建注册表单
  Widget _buildRegisterForm() {
    return Column(
      children: [
        // 姓名输入框
        TextFormField(
          controller: _nameController,
          decoration: InputDecoration(
            labelText: '姓名',
            hintText: '请输入您的姓名',
            prefixIcon: const Icon(Icons.person_outlined),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.borderColor,
                width: 1.5,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.primaryColor,
                width: 2,
              ),
            ),
          ),
          validator: MultiValidator([
            RequiredValidator(errorText: ErrorMessages.nameRequired),
            MinLengthValidator(2, errorText: '姓名至少2个字符'),
          ]),
        ),
        
        SizedBox(height: 16.h),
        
        // 角色选择
        DropdownButtonFormField<String>(
          value: _selectedRole,
          decoration: InputDecoration(
            labelText: '角色',
            prefixIcon: const Icon(Icons.work_outlined),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.borderColor,
                width: 1.5,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.primaryColor,
                width: 2,
              ),
            ),
          ),
          items: _roles.map((String role) {
            return DropdownMenuItem<String>(
              value: role,
              child: Text(role),
            );
          }).toList(),
          onChanged: (String? newValue) {
            AppLogger.debug('RegisterPage: 用户选择角色', {'role': newValue});
            setState(() {
              _selectedRole = newValue!;
            });
          },
        ),
        
        SizedBox(height: 16.h),
        
        // 邮箱输入框
        TextFormField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          decoration: InputDecoration(
            labelText: '邮箱地址',
            hintText: '请输入您的邮箱地址',
            prefixIcon: const Icon(Icons.email_outlined),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.borderColor,
                width: 1.5,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.primaryColor,
                width: 2,
              ),
            ),
          ),
          validator: MultiValidator([
            RequiredValidator(errorText: ErrorMessages.emailRequired),
            EmailValidator(errorText: ErrorMessages.emailInvalid),
          ]),
        ),
        
        SizedBox(height: 16.h),
        
        // 手机号输入框
        TextFormField(
          controller: _phoneController,
          keyboardType: TextInputType.phone,
          decoration: InputDecoration(
            labelText: '手机号',
            hintText: '请输入您的手机号',
            prefixIcon: const Icon(Icons.phone_outlined),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.borderColor,
                width: 1.5,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.primaryColor,
                width: 2,
              ),
            ),
          ),
          validator: MultiValidator([
            RequiredValidator(errorText: '请输入手机号'),
            PatternValidator(r'^1[3-9]\d{9}$', errorText: '请输入正确的手机号'),
          ]),
        ),
        
        SizedBox(height: 16.h),
        
        // 密码输入框
        TextFormField(
          controller: _passwordController,
          obscureText: !_isPasswordVisible,
          decoration: InputDecoration(
            labelText: '密码',
            hintText: '请输入密码（至少6位）',
            prefixIcon: const Icon(Icons.lock_outlined),
            suffixIcon: IconButton(
              icon: Icon(
                _isPasswordVisible
                    ? Icons.visibility_outlined
                    : Icons.visibility_off_outlined,
              ),
              onPressed: () {
                AppLogger.debug('RegisterPage: 用户切换密码可见性', {'visible': !_isPasswordVisible});
                setState(() {
                  _isPasswordVisible = !_isPasswordVisible;
                });
              },
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.borderColor,
                width: 1.5,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.primaryColor,
                width: 2,
              ),
            ),
          ),
          validator: MultiValidator([
            RequiredValidator(errorText: ErrorMessages.passwordRequired),
            MinLengthValidator(6, errorText: ErrorMessages.passwordTooShort),
          ]),
        ),
        
        SizedBox(height: 16.h),
        
        // 确认密码输入框
        TextFormField(
          controller: _confirmPasswordController,
          obscureText: !_isConfirmPasswordVisible,
          decoration: InputDecoration(
            labelText: '确认密码',
            hintText: '请再次输入密码',
            prefixIcon: const Icon(Icons.lock_outlined),
            suffixIcon: IconButton(
              icon: Icon(
                _isConfirmPasswordVisible
                    ? Icons.visibility_outlined
                    : Icons.visibility_off_outlined,
              ),
              onPressed: () {
                AppLogger.debug('RegisterPage: 用户切换确认密码可见性', {'visible': !_isConfirmPasswordVisible});
                setState(() {
                  _isConfirmPasswordVisible = !_isConfirmPasswordVisible;
                });
              },
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.borderColor,
                width: 1.5,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12.r),
              borderSide: BorderSide(
                color: AppTheme.primaryColor,
                width: 2,
              ),
            ),
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              return '请确认密码';
            }
            if (value != _passwordController.text) {
              return ErrorMessages.passwordMismatch;
            }
            return null;
          },
        ),
      ],
    );
  }

  /// 构建用户协议
  Widget _buildTermsAgreement() {
    return Row(
      children: [
        Checkbox(
          value: _agreeToTerms,
          onChanged: (value) {
            final newValue = value ?? false;
            AppLogger.debug('RegisterPage: 用户切换用户协议同意状态', {'agreeToTerms': newValue});
            setState(() {
              _agreeToTerms = newValue;
            });
          },
          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
        ),
        Expanded(
          child: Row(
            children: [
              Text(
                '我已阅读并同意',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
              GestureDetector(
                onTap: _showTermsDialog,
                child: Text(
                  '《用户协议》',
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: AppTheme.primaryColor,
                    decoration: TextDecoration.underline,
                  ),
                ),
              ),
              Text(
                '和',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
              GestureDetector(
                onTap: _showTermsDialog,
                child: Text(
                  '《隐私政策》',
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: AppTheme.primaryColor,
                    decoration: TextDecoration.underline,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// 构建注册按钮
  Widget _buildRegisterButton() {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        return SizedBox(
          width: double.infinity,
          height: 50.h,
          child: ElevatedButton(
            onPressed: authProvider.isLoading ? null : _handleRegister,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primaryColor,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.r),
              ),
              elevation: 2,
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
                    '注册',
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
          ),
        );
      },
    );
  }

  /// 构建登录链接
  Widget _buildLoginLink() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          '已有账户？',
          style: TextStyle(
            fontSize: 14.sp,
            color: AppTheme.textSecondaryColor,
          ),
        ),
        TextButton(
          onPressed: _navigateToLogin,
          child: Text(
            '立即登录',
            style: TextStyle(
              fontSize: 14.sp,
              color: AppTheme.primaryColor,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }
}
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

class ForgotPasswordPage extends StatefulWidget {
  const ForgotPasswordPage({super.key});

  @override
  State<ForgotPasswordPage> createState() => _ForgotPasswordPageState();
}

class _ForgotPasswordPageState extends State<ForgotPasswordPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  bool _isEmailSent = false;

  @override
  void initState() {
    super.initState();
    AppLogger.info('ForgotPasswordPage: 页面初始化');
  }

  @override
  void dispose() {
    AppLogger.debug('ForgotPasswordPage: 页面销毁，清理资源');
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _handleForgotPassword() async {
    AppLogger.info('ForgotPasswordPage: 用户点击忘记密码按钮');
    
    if (!_formKey.currentState!.validate()) {
      AppLogger.warning('ForgotPasswordPage: 表单验证失败');
      return;
    }

    final email = _emailController.text.trim();
    AppLogger.debug('ForgotPasswordPage: 表单验证通过，开始发送重置密码邮件', {'email': email});

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    
    try {
      final success = await authProvider.forgotPassword(email);

      if (success && mounted) {
        AppLogger.info('ForgotPasswordPage: 重置密码邮件发送成功', {'email': email});
        setState(() {
          _isEmailSent = true;
        });
        _showSuccessSnackBar('重置密码邮件已发送，请检查您的邮箱');
      } else if (mounted) {
        final errorMessage = authProvider.errorMessage ?? '发送失败';
        AppLogger.warning('ForgotPasswordPage: 重置密码邮件发送失败', {'email': email, 'error': errorMessage});
        _showErrorSnackBar(errorMessage);
      }
    } catch (e, stackTrace) {
      AppLogger.error('ForgotPasswordPage: 发送重置密码邮件过程中发生异常 - email: $email', e, stackTrace);
      if (mounted) {
        _showErrorSnackBar('发送过程中发生错误');
      }
    }
  }

  /// 显示成功提示
  void _showSuccessSnackBar(String message) {
    AppLogger.debug('ForgotPasswordPage: 显示成功提示', {'message': message});
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        behavior: SnackBarBehavior.floating,
        margin: EdgeInsets.all(UIConstants.paddingMedium.w),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(UIConstants.radiusMedium.r),
        ),
      ),
    );
  }

  /// 显示错误提示
  void _showErrorSnackBar(String message) {
    AppLogger.debug('ForgotPasswordPage: 显示错误提示', {'message': message});
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
    AppLogger.info('ForgotPasswordPage: 用户点击返回登录，导航到登录页面');
    context.go(AppRouter.login);
  }

  /// 重新发送邮件
  void _resendEmail() {
    AppLogger.info('ForgotPasswordPage: 用户点击重新发送邮件');
    setState(() {
      _isEmailSent = false;
    });
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
        title: const Text('忘记密码'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.all(24.w),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(height: 40.h),
              
              // 头部信息
              _buildHeader(),
              
              SizedBox(height: 60.h),
              
              if (!_isEmailSent) ...[
                // 邮箱输入表单
                _buildEmailForm(),
                
                SizedBox(height: 32.h),
                
                // 发送按钮
                _buildSendButton(),
              ] else ...[
                // 邮件发送成功提示
                _buildEmailSentContent(),
              ],
              
              SizedBox(height: 32.h),
              
              // 返回登录链接
              _buildBackToLoginLink(),
            ],
          ),
        ),
      ),
    );
  }

  /// 构建头部
  Widget _buildHeader() {
    return Column(
      children: [
        // 图标
        Container(
          width: 80.w,
          height: 80.w,
          decoration: BoxDecoration(
            color: AppTheme.primaryColor.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(
            _isEmailSent ? Icons.mark_email_read_outlined : Icons.lock_reset,
            size: 40.w,
            color: AppTheme.primaryColor,
          ),
        ),
        
        SizedBox(height: 24.h),
        
        Text(
          _isEmailSent ? '邮件已发送' : '重置密码',
          style: TextStyle(
            fontSize: 28.sp,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimaryColor,
          ),
        ),
        
        SizedBox(height: 8.h),
        
        Text(
          _isEmailSent 
              ? '我们已向您的邮箱发送了重置密码的链接'
              : '请输入您的邮箱地址，我们将发送重置密码的链接',
          style: TextStyle(
            fontSize: 16.sp,
            color: AppTheme.textSecondaryColor,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  /// 构建邮箱输入表单
  Widget _buildEmailForm() {
    return Form(
      key: _formKey,
      child: TextFormField(
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
    );
  }

  /// 构建发送按钮
  Widget _buildSendButton() {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        return SizedBox(
          width: double.infinity,
          height: 50.h,
          child: ElevatedButton(
            onPressed: authProvider.isLoading ? null : _handleForgotPassword,
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
                    '发送重置链接',
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

  /// 构建邮件发送成功内容
  Widget _buildEmailSentContent() {
    return Column(
      children: [
        Container(
          padding: EdgeInsets.all(20.w),
          decoration: BoxDecoration(
            color: Colors.green.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12.r),
            border: Border.all(
              color: Colors.green.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: Column(
            children: [
              Icon(
                Icons.check_circle_outline,
                size: 48.w,
                color: Colors.green,
              ),
              SizedBox(height: 16.h),
              Text(
                '重置链接已发送',
                style: TextStyle(
                  fontSize: 18.sp,
                  fontWeight: FontWeight.w600,
                  color: Colors.green,
                ),
              ),
              SizedBox(height: 8.h),
              Text(
                '请检查您的邮箱 ${_emailController.text}\n并点击链接重置密码',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: AppTheme.textSecondaryColor,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
        
        SizedBox(height: 24.h),
        
        // 重新发送按钮
        TextButton(
          onPressed: _resendEmail,
          child: Text(
            '没有收到邮件？重新发送',
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

  /// 构建返回登录链接
  Widget _buildBackToLoginLink() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.arrow_back,
          size: 16.w,
          color: AppTheme.textSecondaryColor,
        ),
        SizedBox(width: 8.w),
        TextButton(
          onPressed: _navigateToLogin,
          child: Text(
            '返回登录',
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
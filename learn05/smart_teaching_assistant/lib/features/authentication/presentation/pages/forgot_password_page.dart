import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../../models/auth_dto.dart';
import '../../../../shared/widgets/custom_text_field.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_text_styles.dart';
import '../../../../core/constants/app_dimensions.dart';

/// 忘记密码页面
class ForgotPasswordPage extends StatefulWidget {
  const ForgotPasswordPage({super.key});

  @override
  State<ForgotPasswordPage> createState() => _ForgotPasswordPageState();
}

class _ForgotPasswordPageState extends State<ForgotPasswordPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _codeController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  
  int _currentStep = 0; // 0: 邮箱输入, 1: 验证码验证, 2: 密码重置
  int _countdown = 0;
  
  @override
  void dispose() {
    _emailController.dispose();
    _codeController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }
  
  void _startCountdown() {
    setState(() {
      _countdown = 60;
    });
    
    Future.doWhile(() async {
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) {
        setState(() {
          _countdown--;
        });
        return _countdown > 0;
      }
      return false;
    });
  }
  
  Future<void> _sendVerificationCode() async {
    if (!_formKey.currentState!.validate()) return;
    
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    
    try {
      await authProvider.sendPasswordResetEmail(_emailController.text.trim());
      
      setState(() {
        _currentStep = 1;
      });
      
      _startCountdown();
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('验证码已发送到您的邮箱'),
            backgroundColor: AppColors.success,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('发送失败: $e'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }
  
  Future<void> _verifyCode() async {
    if (_codeController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('请输入验证码'),
          backgroundColor: AppColors.warning,
        ),
      );
      return;
    }
    
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    
    try {
      final isValid = await authProvider.verifyCode(
        identifier: _emailController.text.trim(),
        code: _codeController.text.trim(),
        type: VerificationType.email,
        purpose: VerificationPurpose.passwordReset,
      );
      
      if (isValid) {
        setState(() {
          _currentStep = 2;
        });
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('验证码验证成功'),
              backgroundColor: AppColors.success,
            ),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('验证码错误'),
              backgroundColor: AppColors.error,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('验证失败: $e'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }
  
  Future<void> _resetPassword() async {
    if (!_formKey.currentState!.validate()) return;
    
    if (_passwordController.text != _confirmPasswordController.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('两次输入的密码不一致'),
          backgroundColor: AppColors.warning,
        ),
      );
      return;
    }
    
    try {
      // 模拟密码重置成功
      await Future.delayed(const Duration(seconds: 1));
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('密码重置成功'),
            backgroundColor: AppColors.success,
          ),
        );
        
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('重置失败: $e'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(
          '重置密码',
          style: AppTextStyles.headlineMedium.copyWith(color: AppColors.textPrimary),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppDimensions.paddingLarge),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: AppDimensions.spacingLarge),
                
                // 步骤指示器
                _buildStepIndicator(),
                
                const SizedBox(height: AppDimensions.spacingXLarge),
                
                // 标题和描述
                _buildHeader(),
                
                const SizedBox(height: AppDimensions.spacingXLarge),
                
                // 表单内容
                _buildFormContent(),
                
                const SizedBox(height: AppDimensions.spacingXLarge),
                
                // 操作按钮
                _buildActionButtons(),
                
                const SizedBox(height: AppDimensions.spacingLarge),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildStepIndicator() {
    return Row(
      children: [
        _buildStepItem(0, '邮箱验证', Icons.email),
        _buildStepConnector(0),
        _buildStepItem(1, '验证码', Icons.security),
        _buildStepConnector(1),
        _buildStepItem(2, '重置密码', Icons.lock_reset),
      ],
    );
  }
  
  Widget _buildStepItem(int step, String title, IconData icon) {
    final isActive = _currentStep >= step;
    final isCurrent = _currentStep == step;
    
    return Expanded(
      child: Column(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isActive ? AppColors.primary : AppColors.surfaceVariant,
              border: isCurrent
                  ? Border.all(color: AppColors.primary, width: 2)
                  : null,
            ),
            child: Icon(
              icon,
              color: isActive ? Colors.white : AppColors.textSecondary,
              size: 20,
            ),
          ),
          const SizedBox(height: AppDimensions.spacingTiny),
          Text(
            title,
            style: AppTextStyles.caption.copyWith(
              color: isActive ? AppColors.primary : AppColors.textSecondary,
              fontWeight: isCurrent ? FontWeight.w600 : FontWeight.normal,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
  
  Widget _buildStepConnector(int step) {
    final isCompleted = _currentStep > step;
    
    return Expanded(
      child: Container(
        height: 2,
        margin: const EdgeInsets.only(bottom: 24),
        color: isCompleted ? AppColors.primary : AppColors.surfaceVariant,
      ),
    );
  }
  
  Widget _buildHeader() {
    String title;
    String description;
    
    switch (_currentStep) {
      case 0:
        title = '输入邮箱地址';
        description = '请输入您注册时使用的邮箱地址，我们将向您发送验证码';
        break;
      case 1:
        title = '验证邮箱';
        description = '请输入发送到您邮箱的6位验证码';
        break;
      case 2:
        title = '设置新密码';
        description = '请设置您的新密码，密码长度至少8位';
        break;
      default:
        title = '';
        description = '';
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: AppTextStyles.headlineLarge.copyWith(color: AppColors.textPrimary),
        ),
        const SizedBox(height: AppDimensions.spacingSmall),
        Text(
          description,
          style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSecondary),
        ),
      ],
    );
  }
  
  Widget _buildFormContent() {
    switch (_currentStep) {
      case 0:
        return _buildEmailStep();
      case 1:
        return _buildCodeStep();
      case 2:
        return _buildPasswordStep();
      default:
        return const SizedBox.shrink();
    }
  }
  
  Widget _buildEmailStep() {
    return CustomTextField(
      controller: _emailController,
      labelText: '邮箱地址',
      hintText: '请输入邮箱地址',
      prefixIcon: Icons.email_outlined,
      keyboardType: TextInputType.emailAddress,
      validator: (value) {
        if (value == null || value.trim().isEmpty) {
          return '请输入邮箱地址';
        }
        if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
          return '请输入有效的邮箱地址';
        }
        return null;
      },
    );
  }
  
  Widget _buildCodeStep() {
    return Column(
      children: [
        CustomTextField(
          controller: _codeController,
          labelText: '验证码',
          hintText: '请输入6位验证码',
          prefixIcon: Icons.security,
          keyboardType: TextInputType.number,
          maxLength: 6,
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return '请输入验证码';
            }
            if (value.length != 6) {
              return '验证码必须是6位数字';
            }
            return null;
          },
        ),
        const SizedBox(height: AppDimensions.spacingMedium),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '没有收到验证码？',
              style: AppTextStyles.bodyMedium.copyWith(color: AppColors.textSecondary),
            ),
            TextButton(
              onPressed: _countdown > 0 ? null : _sendVerificationCode,
              child: Text(
                _countdown > 0 ? '重新发送(${_countdown}s)' : '重新发送',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: _countdown > 0 ? AppColors.textSecondary : AppColors.primary,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
  
  Widget _buildPasswordStep() {
    return Column(
      children: [
        CustomTextField(
          controller: _passwordController,
          labelText: '新密码',
          hintText: '请输入新密码',
          prefixIcon: Icons.lock_outlined,
          obscureText: true,
          validator: (value) {
            if (value == null || value.isEmpty) {
              return '请输入密码';
            }
            if (value.length < 8) {
              return '密码长度至少8位';
            }
            return null;
          },
        ),
        const SizedBox(height: AppDimensions.spacingMedium),
        CustomTextField(
          controller: _confirmPasswordController,
          labelText: '确认密码',
          hintText: '请再次输入密码',
          prefixIcon: Icons.lock_outlined,
          obscureText: true,
          validator: (value) {
            if (value == null || value.isEmpty) {
              return '请确认密码';
            }
            if (value != _passwordController.text) {
              return '两次输入的密码不一致';
            }
            return null;
          },
        ),
      ],
    );
  }
  
  Widget _buildActionButtons() {
    return Consumer<AuthProvider>(builder: (context, authProvider, child) {
      return Column(
        children: [
          CustomButton(
            text: _getButtonText(),
            onPressed: _getButtonAction(),
            isLoading: authProvider.isLoading,
            expanded: true,
            type: ButtonType.primary,
          ),
          if (_currentStep > 0)
            const SizedBox(height: AppDimensions.spacingMedium),
          if (_currentStep > 0)
            CustomButton(
              text: '上一步',
              onPressed: () {
                setState(() {
                  _currentStep--;
                });
              },
              expanded: true,
              type: ButtonType.outline,
            ),
        ],
      );
    });
  }
  
  String _getButtonText() {
    switch (_currentStep) {
      case 0:
        return '发送验证码';
      case 1:
        return '验证';
      case 2:
        return '重置密码';
      default:
        return '';
    }
  }
  
  VoidCallback? _getButtonAction() {
    switch (_currentStep) {
      case 0:
        return _sendVerificationCode;
      case 1:
        return _verifyCode;
      case 2:
        return _resetPassword;
      default:
        return null;
    }
  }
}
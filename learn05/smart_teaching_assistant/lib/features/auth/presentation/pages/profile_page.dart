import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/utils/app_logger.dart';
// 移除不存在的导入

class ProfilePage extends StatefulWidget {
  const ProfilePage({Key? key}) : super(key: key);

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _currentPasswordController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  
  bool _isEditing = false;
  bool _isChangingPassword = false;
  bool _isLoading = false;
  
  @override
  void initState() {
    super.initState();
    AppLogger.info('ProfilePage: 页面初始化');
    _loadUserData();
  }
  
  void _loadUserData() {
    AppLogger.info('ProfilePage: 开始加载用户数据');
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final user = authProvider.user;
    if (user != null) {
      _nameController.text = user.realName ?? '';
      _emailController.text = user.email;
      _phoneController.text = user.profile?['phone'] ?? '';
      AppLogger.info('ProfilePage: 用户数据加载成功', {
        'userId': user.id,
        'userName': user.realName ?? user.username,
        'userEmail': user.email
      });
    } else {
      AppLogger.warning('ProfilePage: 用户数据为空');
    }
  }
  
  @override
  void dispose() {
    AppLogger.info('ProfilePage: 页面销毁，清理资源');
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _currentPasswordController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }
  
  Future<void> _updateProfile() async {
    AppLogger.info('ProfilePage: 用户点击更新个人资料');
    
    if (!_formKey.currentState!.validate()) {
      AppLogger.warning('ProfilePage: 个人资料表单验证失败');
      return;
    }
    
    setState(() {
      _isLoading = true;
    });
    
    try {
      final profileData = {
        'name': _nameController.text.trim(),
        'phone': _phoneController.text.trim(),
      };
      
      AppLogger.info('ProfilePage: 准备更新个人资料', profileData);
      
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final success = await authProvider.updateProfile(profileData);
      
      if (success) {
        AppLogger.info('ProfilePage: 个人资料更新成功');
        setState(() {
          _isEditing = false;
        });
        _showSuccessSnackBar('个人资料更新成功');
      } else {
        AppLogger.error('ProfilePage: 个人资料更新失败', authProvider.errorMessage ?? '更新失败');
        _showErrorSnackBar(authProvider.errorMessage ?? '更新失败');
      }
    } catch (e, stackTrace) {
      AppLogger.error('ProfilePage: 个人资料更新异常', e, stackTrace);
      _showErrorSnackBar('更新失败：$e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
  
  Future<void> _changePassword() async {
    AppLogger.info('ProfilePage: 用户点击修改密码');
    
    if (!_formKey.currentState!.validate()) {
      AppLogger.warning('ProfilePage: 密码修改表单验证失败');
      return;
    }
    
    if (_newPasswordController.text != _confirmPasswordController.text) {
      AppLogger.warning('ProfilePage: 新密码和确认密码不匹配');
      _showErrorSnackBar('新密码和确认密码不匹配');
      return;
    }
    
    setState(() {
      _isLoading = true;
    });
    
    try {
      AppLogger.info('ProfilePage: 准备修改密码');
      
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final success = await authProvider.changePassword(
        _currentPasswordController.text,
        _newPasswordController.text,
      );
      
      if (success) {
        AppLogger.info('ProfilePage: 密码修改成功');
        setState(() {
          _isChangingPassword = false;
        });
        _currentPasswordController.clear();
        _newPasswordController.clear();
        _confirmPasswordController.clear();
        _showSuccessSnackBar('密码修改成功');
      } else {
        AppLogger.error('ProfilePage: 密码修改失败', authProvider.errorMessage ?? '密码修改失败');
        _showErrorSnackBar(authProvider.errorMessage ?? '密码修改失败');
      }
    } catch (e, stackTrace) {
      AppLogger.error('ProfilePage: 密码修改异常', e, stackTrace);
      _showErrorSnackBar('密码修改失败：$e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
  
  void _showErrorSnackBar(String message) {
    AppLogger.info('ProfilePage: 显示错误提示', {'message': message});
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }
  
  void _showSuccessSnackBar(String message) {
    AppLogger.info('ProfilePage: 显示成功提示', {'message': message});
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
      ),
    );
  }
  
  void _logout() {
    AppLogger.info('ProfilePage: 用户点击退出登录');
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认退出'),
        content: const Text('您确定要退出登录吗？'),
        actions: [
          TextButton(
            onPressed: () {
              AppLogger.info('ProfilePage: 用户取消退出登录');
              Navigator.of(context).pop();
            },
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              AppLogger.info('ProfilePage: 用户确认退出登录');
              Navigator.of(context).pop();
              Provider.of<AuthProvider>(context, listen: false).logout();
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('个人资料'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          if (!_isEditing && !_isChangingPassword)
            IconButton(
              onPressed: () {
                setState(() {
                  _isEditing = true;
                });
              },
              icon: const Icon(Icons.edit),
            ),
          IconButton(
            onPressed: _logout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Form(
              key: _formKey,
              child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 用户头像
                Center(
                  child: CircleAvatar(
                    radius: 50,
                    backgroundColor: Colors.blue,
                    child: Icon(
                      Icons.person,
                      size: 50,
                      color: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                
                // 基本信息
                Text(
                  '基本信息',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 16),
                
                TextFormField(
                  controller: _nameController,
                  decoration: InputDecoration(
                    labelText: '姓名',
                    prefixIcon: Icon(Icons.person),
                    border: OutlineInputBorder(),
                  ),
                  enabled: _isEditing,
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return '请输入姓名';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                
                TextFormField(
                  controller: _emailController,
                  decoration: InputDecoration(
                    labelText: '邮箱',
                    prefixIcon: Icon(Icons.email),
                    border: OutlineInputBorder(),
                  ),
                  enabled: false, // 邮箱不允许修改
                  keyboardType: TextInputType.emailAddress,
                ),
                const SizedBox(height: 16),
                
                TextFormField(
                  controller: _phoneController,
                  decoration: InputDecoration(
                    labelText: '手机号',
                    prefixIcon: Icon(Icons.phone),
                    border: OutlineInputBorder(),
                  ),
                  enabled: _isEditing,
                  keyboardType: TextInputType.phone,
                  validator: (value) {
                    if (value != null && value.isNotEmpty) {
                      if (!RegExp(r'^1[3-9]\d{9}$').hasMatch(value)) {
                        return '请输入有效的手机号';
                      }
                    }
                    return null;
                  },
                ),
                
                if (_isEditing) ...[
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            setState(() {
                              _isEditing = false;
                            });
                            _loadUserData(); // 重新加载数据
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.grey,
                          ),
                          child: const Text('取消'),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: _updateProfile,
                          child: const Text('保存'),
                        ),
                      ),
                    ],
                  ),
                ],
                
                const SizedBox(height: 32),
                
                // 密码修改
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '密码管理',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                    if (!_isChangingPassword && !_isEditing)
                      TextButton(
                        onPressed: () {
                          setState(() {
                            _isChangingPassword = true;
                          });
                        },
                        child: const Text('修改密码'),
                      ),
                  ],
                ),
                
                if (_isChangingPassword) ...[
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _currentPasswordController,
                    decoration: InputDecoration(
                      labelText: '当前密码',
                      prefixIcon: Icon(Icons.lock),
                      border: OutlineInputBorder(),
                    ),
                    obscureText: true,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入当前密码';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  
                  TextFormField(
                    controller: _newPasswordController,
                    decoration: InputDecoration(
                      labelText: '新密码',
                      prefixIcon: Icon(Icons.lock_outline),
                      border: OutlineInputBorder(),
                    ),
                    obscureText: true,
                    validator: (value) {
                      if (value == null || value.length < 6) {
                        return '密码长度至少6位';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  
                  TextFormField(
                    controller: _confirmPasswordController,
                    decoration: InputDecoration(
                      labelText: '确认新密码',
                      prefixIcon: Icon(Icons.lock_outline),
                      border: OutlineInputBorder(),
                    ),
                    obscureText: true,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请确认新密码';
                      }
                      if (value != _newPasswordController.text) {
                        return '两次输入的密码不一致';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 24),
                  
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            setState(() {
                              _isChangingPassword = false;
                            });
                            _currentPasswordController.clear();
                            _newPasswordController.clear();
                            _confirmPasswordController.clear();
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.grey,
                          ),
                          child: const Text('取消'),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: _changePassword,
                          child: const Text('修改密码'),
                        ),
                      ),
                    ],
                  ),
                ],
                
                const SizedBox(height: 32),
              ],
            ),
          ),
          ),
          if (_isLoading)
            Container(
              color: Colors.black26,
              child: const Center(
                child: CircularProgressIndicator(),
              ),
            ),
        ],
      ),
    );
  }
}
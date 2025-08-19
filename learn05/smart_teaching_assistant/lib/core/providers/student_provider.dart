import 'package:flutter/foundation.dart';

import '../data/repositories/student_repository.dart';
import '../models/student_model.dart';
import '../services/connectivity_service.dart';
import '../utils/app_logger.dart';

/// 学生数据提供者
/// 负责管理学生相关的状态和业务逻辑
class StudentProvider extends ChangeNotifier {
  final StudentRepository _studentRepository;
  final ConnectivityService _connectivityService;

  // 状态管理
  bool _isLoading = false;
  String? _error;
  List<Student> _students = [];
  List<Student> _filteredStudents = [];
  StudentStatistics? _statistics;

  // 筛选和分页
  int _currentPage = 1;
  int _pageSize = 20;
  String? _selectedClassId;
  String? _selectedGrade;
  String _searchQuery = '';
  String _sortBy = 'name';
  bool _sortAscending = true;

  StudentProvider({
    required StudentRepository studentRepository,
    required ConnectivityService connectivityService,
  }) : _studentRepository = studentRepository,
       _connectivityService = connectivityService;

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<Student> get students => _filteredStudents;
  StudentStatistics? get statistics => _statistics;
  int get currentPage => _currentPage;
  int get pageSize => _pageSize;
  String? get selectedClassId => _selectedClassId;
  String? get selectedGrade => _selectedGrade;
  String get searchQuery => _searchQuery;
  String get sortBy => _sortBy;
  bool get sortAscending => _sortAscending;
  bool get hasError => _error != null;
  bool get isEmpty => _students.isEmpty && !_isLoading;
  bool get isNotEmpty => _students.isNotEmpty;
  String? get errorMessage => _error;

  /// 加载学生数据
  Future<void> loadStudents({bool forceRefresh = false}) async {
    if (_isLoading) return;

    _setLoading(true);
    _clearError();

    try {
      final response = await _studentRepository.getStudents(
        page: _currentPage,
        pageSize: _pageSize,
        classId: _selectedClassId,
        grade: _selectedGrade,
        forceRefresh: forceRefresh,
      );

      if (response.success && response.data != null) {
        _students = response.data!.items;
        _applyFilters();
        AppLogger.info('学生数据加载成功: ${_students.length}条记录');
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('学生数据加载失败: ${response.message}');
      }
    } catch (e) {
      _setError('加载学生数据时发生错误');
      AppLogger.error('加载学生数据异常', e);
    } finally {
      _setLoading(false);
    }
  }

  /// 加载学生统计数据
  Future<void> loadStatistics({bool forceRefresh = false}) async {
    try {
      final response = await _studentRepository.getStudentStatistics(
        classId: _selectedClassId,
        grade: _selectedGrade,
      );

      if (response.success && response.data != null) {
        _statistics = response.data!;
        notifyListeners();
        AppLogger.info('学生统计数据加载成功');
      } else {
        AppLogger.error('学生统计数据加载失败: ${response.message}');
      }
    } catch (e) {
      AppLogger.error('加载学生统计数据异常', e);
    }
  }

  /// 创建学生记录
  Future<bool> createStudent(Map<String, dynamic> studentData) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _studentRepository.createStudent(studentData);
      
      if (response.success && response.data != null) {
        _students.add(response.data!);
        _applyFilters();
        await loadStatistics(); // 刷新统计数据
        AppLogger.info('学生记录创建成功: ${studentData['name']}');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('学生记录创建失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('创建学生记录时发生错误');
      AppLogger.error('创建学生记录异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 更新学生记录
  Future<bool> updateStudent(String studentId, Map<String, dynamic> studentData) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _studentRepository.updateStudent(studentId, studentData);
      
      if (response.success && response.data != null) {
        final index = _students.indexWhere((s) => s.id == studentId);
        if (index != -1) {
          _students[index] = response.data!;
          _applyFilters();
          await loadStatistics(); // 刷新统计数据
          AppLogger.info('学生记录更新成功: ${studentData['name']}');
          return true;
        }
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('学生记录更新失败: ${response.message}');
      }
      return false;
    } catch (e) {
      _setError('更新学生记录时发生错误');
      AppLogger.error('更新学生记录异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 删除学生记录
  Future<bool> deleteStudent(String studentId) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _studentRepository.deleteStudent(studentId);
      
      if (response.success) {
        _students.removeWhere((s) => s.id == studentId);
        _applyFilters();
        await loadStatistics(); // 刷新统计数据
        AppLogger.info('学生记录删除成功');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('学生记录删除失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('删除学生记录时发生错误');
      AppLogger.error('删除学生记录异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 批量导入学生
  Future<bool> importStudents(String filePath) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _studentRepository.importStudents(
        filePath,
        classId: _selectedClassId,
      );
      
      if (response.success) {
        await loadStudents(forceRefresh: true); // 重新加载数据
        await loadStatistics(forceRefresh: true);
        AppLogger.info('学生数据导入成功');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('学生数据导入失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('导入学生数据时发生错误');
      AppLogger.error('导入学生数据异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 导出学生数据
  Future<String?> exportStudents({String format = 'excel'}) async {
    if (_isLoading) return null;

    _setLoading(true);
    _clearError();

    try {
      final response = await _studentRepository.exportStudents(
        classId: _selectedClassId,
        grade: _selectedGrade,
        format: format,
      );
      
      if (response.success && response.data != null) {
        AppLogger.info('学生数据导出成功: $format格式');
        return response.data!;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('学生数据导出失败: ${response.message}');
        return null;
      }
    } catch (e) {
      _setError('导出学生数据时发生错误');
      AppLogger.error('导出学生数据异常', e);
      return null;
    } finally {
      _setLoading(false);
    }
  }

  /// 获取单个学生详情
  Future<Student?> getStudentDetail(String studentId) async {
    try {
      final response = await _studentRepository.getStudent(studentId);
      
      if (response.success && response.data != null) {
        AppLogger.info('学生详情获取成功: ${response.data!.name}');
        return response.data!;
      } else {
        AppLogger.error('学生详情获取失败: ${response.message}');
        return null;
      }
    } catch (e) {
      AppLogger.error('获取学生详情异常', e);
      return null;
    }
  }

  /// 设置筛选条件
  void setFilters({
    String? classId,
    String? grade,
  }) {
    _selectedClassId = classId;
    _selectedGrade = grade;
    _currentPage = 1; // 重置页码
    notifyListeners();
  }

  /// 设置搜索查询
  void setSearchQuery(String query) {
    _searchQuery = query;
    _applyFilters();
  }

  /// 设置排序
  void setSorting(String sortBy, {bool? ascending}) {
    _sortBy = sortBy;
    if (ascending != null) {
      _sortAscending = ascending;
    } else {
      // 如果是同一个字段，切换排序方向
      _sortAscending = _sortBy == sortBy ? !_sortAscending : true;
    }
    _applySorting();
  }

  /// 设置分页
  void setPage(int page) {
    _currentPage = page;
    notifyListeners();
  }

  /// 设置每页大小
  void setPageSize(int pageSize) {
    _pageSize = pageSize;
    _currentPage = 1; // 重置页码
    notifyListeners();
  }

  /// 清除筛选条件
  void clearFilters() {
    _selectedClassId = null;
    _selectedGrade = null;
    _searchQuery = '';
    _currentPage = 1;
    _applyFilters();
  }

  /// 刷新数据
  Future<void> refresh() async {
    await Future.wait([
      loadStudents(forceRefresh: true),
      loadStatistics(forceRefresh: true),
    ]);
  }

  /// 应用筛选
  void _applyFilters() {
    _filteredStudents = _students.where((student) {
      // 搜索筛选
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        if (!student.name.toLowerCase().contains(query) &&
            !student.studentNumber.toLowerCase().contains(query) &&
            !(student.email?.toLowerCase().contains(query) ?? false)) {
          return false;
        }
      }
      return true;
    }).toList();
    
    _applySorting();
  }

  /// 应用排序
  void _applySorting() {
    _filteredStudents.sort((a, b) {
      int comparison = 0;
      
      switch (_sortBy) {
        case 'name':
          comparison = a.name.compareTo(b.name);
          break;
        case 'studentNumber':
          comparison = a.studentNumber.compareTo(b.studentNumber);
          break;
        case 'grade':
          comparison = (a.grade ?? '').compareTo(b.grade ?? '');
          break;
        case 'className':
          comparison = (a.className ?? '').compareTo(b.className ?? '');
          break;
        case 'createdAt':
          comparison = a.createdAt.compareTo(b.createdAt);
          break;
        default:
          comparison = a.name.compareTo(b.name);
      }
      
      return _sortAscending ? comparison : -comparison;
    });
    
    notifyListeners();
  }

  /// 获取可用的年级列表
  List<String> get availableGrades {
    return _students
        .where((student) => student.grade != null)
        .map((student) => student.grade!)
        .toSet()
        .toList()..sort();
  }

  /// 获取可用的班级列表
  List<String> get availableClasses {
    return _students
        .where((student) => student.className != null)
        .map((student) => student.className!)
        .toSet()
        .toList()..sort();
  }

  /// 获取指定班级的学生
  List<Student> getStudentsByClass(String classId) {
    return _filteredStudents.where((Student student) => student.classId == classId).toList();
  }

  /// 获取指定年级的学生
  List<Student> getStudentsByGrade(String grade) {
    return _filteredStudents.where((Student student) => student.grade == grade).toList();
  }

  /// 根据学号查找学生
  Student? findStudentByNumber(String studentNumber) {
    try {
      return _students.firstWhere((Student student) => student.studentNumber == studentNumber);
    } catch (e) {
      return null;
    }
  }

  /// 根据姓名查找学生
  List<Student> findStudentsByName(String name) {
    final query = name.toLowerCase();
    return _students.where((Student student) => 
        student.name.toLowerCase().contains(query)).toList();
  }

  /// 检查学号是否已存在
  bool isStudentNumberExists(String studentNumber, {String? excludeId}) {
    return _students.any((Student student) => 
        student.studentNumber == studentNumber && student.id != excludeId);
  }

  /// 获取学生总数
  int get totalStudents => _students.length;

  /// 获取筛选后的学生数
  int get filteredStudents => _filteredStudents.length;

  /// 设置加载状态
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  /// 设置错误信息
  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  /// 清除错误信息
  void _clearError() {
    _error = null;
    notifyListeners();
  }

  @override
  void dispose() {
    super.dispose();
  }
}
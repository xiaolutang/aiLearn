import 'package:flutter/foundation.dart';

import '../data/repositories/class_repository.dart';
import '../data/repositories/student_repository.dart';
import '../models/student_model.dart';
import '../services/connectivity_service.dart';
import '../utils/app_logger.dart';

/// 班级数据提供者
/// 负责管理班级相关的状态和业务逻辑
class ClassProvider extends ChangeNotifier {
  final ClassRepository _classRepository;
  final ConnectivityService _connectivityService;

  // 状态管理
  bool _isLoading = false;
  String? _error;
  List<ClassModel> _classes = [];
  List<ClassModel> _filteredClasses = [];
  ClassStatistics? _statistics;
  ClassModel? _selectedClass;

  // 筛选和分页
  int _currentPage = 1;
  int _pageSize = 20;
  String? _selectedGrade;
  String? _selectedTeacherId;
  String _searchQuery = '';
  String _sortBy = 'name';
  bool _sortAscending = true;
  bool? _isActiveFilter;

  ClassProvider({
    required ClassRepository classRepository,
    required ConnectivityService connectivityService,
  }) : _classRepository = classRepository,
       _connectivityService = connectivityService;

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<ClassModel> get classes => _filteredClasses;
  ClassStatistics? get statistics => _statistics;
  ClassModel? get selectedClass => _selectedClass;
  int get currentPage => _currentPage;
  int get pageSize => _pageSize;
  String? get selectedGrade => _selectedGrade;
  String? get selectedTeacherId => _selectedTeacherId;
  String get searchQuery => _searchQuery;
  String get sortBy => _sortBy;
  bool get sortAscending => _sortAscending;
  bool? get isActiveFilter => _isActiveFilter;
  bool get hasError => _error != null;
  bool get isEmpty => _classes.isEmpty && !_isLoading;
  bool get isNotEmpty => _classes.isNotEmpty;

  /// 加载班级数据
  Future<void> loadClasses({bool forceRefresh = false}) async {
    if (_isLoading) return;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.getClasses(
        page: _currentPage,
        pageSize: _pageSize,
        grade: _selectedGrade,
        teacherId: _selectedTeacherId,
        searchQuery: _searchQuery,
        isActive: _isActiveFilter,
        forceRefresh: forceRefresh,
      );

      if (response.success && response.data != null) {
        _classes = response.data!.items;
        _applyFilters();
        AppLogger.info('班级数据加载成功: ${_classes.length}条记录');
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('班级数据加载失败: ${response.message}');
      }
    } catch (e) {
      _setError('加载班级数据时发生错误');
      AppLogger.error('加载班级数据异常', e);
    } finally {
      _setLoading(false);
    }
  }

  /// 加载班级统计数据
  Future<void> loadStatistics({bool forceRefresh = false}) async {
    try {
      final response = await _classRepository.getClassStatistics(
        grade: _selectedGrade,
        teacherId: _selectedTeacherId,
      );

      if (response.success && response.data != null) {
        _statistics = response.data!;
        notifyListeners();
        AppLogger.info('班级统计数据加载成功');
      } else {
        AppLogger.error('班级统计数据加载失败: ${response.message}');
      }
    } catch (e) {
      AppLogger.error('加载班级统计数据异常', e);
    }
  }

  /// 获取单个班级详情
  Future<ClassModel?> getClassDetail(String classId, {bool includeStudents = false}) async {
    try {
      final response = await _classRepository.getClass(classId, includeStudents: includeStudents);
      
      if (response.success && response.data != null) {
        _selectedClass = response.data!;
        notifyListeners();
        AppLogger.info('班级详情获取成功: ${response.data!.name}');
        return response.data!;
      } else {
        AppLogger.error('班级详情获取失败: ${response.message}');
        return null;
      }
    } catch (e) {
      AppLogger.error('获取班级详情异常', e);
      return null;
    }
  }

  /// 根据ID获取班级
  ClassModel? getClassById(String classId) {
    try {
      return _classes.firstWhere((cls) => cls.id == classId);
    } catch (e) {
      return null;
    }
  }

  /// 获取班级列表
  Future<void> fetchClasses() async {
    await loadClasses();
  }

  /// 创建班级记录
  Future<bool> createClass(ClassModel classData) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.createClass(classData.toJson());
      
      if (response.success && response.data != null) {
        _classes.add(response.data!);
        _applyFilters();
        await loadStatistics(); // 刷新统计数据
        AppLogger.info('班级记录创建成功: ${classData.name}');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('班级记录创建失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('创建班级记录时发生错误');
      AppLogger.error('创建班级记录异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 批量创建班级
  Future<bool> createClassesBatch(List<ClassModel> classesData) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.createClassesBatch(
        classesData.map((c) => c.toJson()).toList(),
      );
      
      if (response.success && response.data != null) {
        _classes.addAll(response.data!);
        _applyFilters();
        await loadStatistics(); // 刷新统计数据
        AppLogger.info('批量创建班级成功: ${classesData.length}个班级');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('批量创建班级失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('批量创建班级时发生错误');
      AppLogger.error('批量创建班级异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 更新班级记录
  Future<bool> updateClass(String classId, ClassModel updatedClass) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.updateClass(classId, updatedClass.toJson());
      
      if (response.success && response.data != null) {
        final index = _classes.indexWhere((c) => c.id == classId);
        if (index != -1) {
          _classes[index] = response.data!;
          _applyFilters();
          
          // 更新选中的班级
          if (_selectedClass?.id == classId) {
            _selectedClass = response.data!;
          }
          
          await loadStatistics(); // 刷新统计数据
          AppLogger.info('班级记录更新成功: ${updatedClass.name}');
          return true;
        }
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('班级记录更新失败: ${response.message}');
      }
      return false;
    } catch (e) {
      _setError('更新班级记录时发生错误');
      AppLogger.error('更新班级记录异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 删除班级记录
  Future<bool> deleteClass(String classId) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.deleteClass(classId);
      
      if (response.success) {
        _classes.removeWhere((c) => c.id == classId);
        _applyFilters();
        
        // 清除选中的班级
        if (_selectedClass?.id == classId) {
          _selectedClass = null;
        }
        
        await loadStatistics(); // 刷新统计数据
        AppLogger.info('班级记录删除成功');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('班级记录删除失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('删除班级记录时发生错误');
      AppLogger.error('删除班级记录异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 批量删除班级
  Future<bool> deleteClassesBatch(List<String> classIds) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.deleteClassesBatch(classIds);
      
      if (response.success) {
        _classes.removeWhere((c) => classIds.contains(c.id));
        _applyFilters();
        
        // 清除选中的班级（如果被删除）
        if (_selectedClass != null && classIds.contains(_selectedClass!.id)) {
          _selectedClass = null;
        }
        
        await loadStatistics(); // 刷新统计数据
        AppLogger.info('批量删除班级成功: ${classIds.length}个班级');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('批量删除班级失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('批量删除班级时发生错误');
      AppLogger.error('批量删除班级异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 切换班级状态（激活/停用）
  Future<bool> toggleClassStatus(String classId, bool isActive) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.toggleClassStatus(classId, isActive);
      
      if (response.success) {
        final index = _classes.indexWhere((c) => c.id == classId);
        if (index != -1) {
          _classes[index] = _classes[index].copyWith(isActive: isActive);
          _applyFilters();
          
          // 更新选中的班级
          if (_selectedClass?.id == classId) {
            _selectedClass = _selectedClass!.copyWith(isActive: isActive);
          }
        }
        
        await loadStatistics(); // 刷新统计数据
        AppLogger.info('班级状态切换成功: ${isActive ? "激活" : "停用"}');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('班级状态切换失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('切换班级状态时发生错误');
      AppLogger.error('切换班级状态异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 获取班级学生列表
  Future<List<Student>?> getClassStudents(String classId) async {
    try {
      final response = await _classRepository.getClassStudents(classId);
      
      if (response.success && response.data != null) {
        AppLogger.info('班级学生列表获取成功: ${response.data!.length}名学生');
        return response.data!;
      } else {
        AppLogger.error('班级学生列表获取失败: ${response.message}');
        return null;
      }
    } catch (e) {
      AppLogger.error('获取班级学生列表异常', e);
      return null;
    }
  }

  /// 添加学生到班级
  Future<bool> addStudentToClass(String classId, String studentId) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.addStudentToClass(classId, studentId);
      
      if (response.success) {
        // 更新班级学生数量
        final index = _classes.indexWhere((c) => c.id == classId);
        if (index != -1) {
          _classes[index] = _classes[index].copyWith(
            studentCount: _classes[index].studentCount + 1,
          );
          _applyFilters();
        }
        
        AppLogger.info('学生添加到班级成功');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('学生添加到班级失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('添加学生到班级时发生错误');
      AppLogger.error('添加学生到班级异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 从班级移除学生
  Future<bool> removeStudentFromClass(String classId, String studentId) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.removeStudentFromClass(classId, studentId);
      
      if (response.success) {
        // 更新班级学生数量
        final index = _classes.indexWhere((c) => c.id == classId);
        if (index != -1) {
          _classes[index] = _classes[index].copyWith(
            studentCount: _classes[index].studentCount - 1,
          );
          _applyFilters();
        }
        
        AppLogger.info('学生从班级移除成功');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('学生从班级移除失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('从班级移除学生时发生错误');
      AppLogger.error('从班级移除学生异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 批量添加学生到班级
  Future<bool> addStudentsToClass(String classId, List<String> studentIds) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.addStudentsToClass(classId, studentIds);
      
      if (response.success) {
        // 更新班级学生数量
        final index = _classes.indexWhere((c) => c.id == classId);
        if (index != -1) {
          _classes[index] = _classes[index].copyWith(
            studentCount: _classes[index].studentCount + studentIds.length,
          );
          _applyFilters();
        }
        
        AppLogger.info('批量添加学生到班级成功: ${studentIds.length}名学生');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('批量添加学生到班级失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('批量添加学生到班级时发生错误');
      AppLogger.error('批量添加学生到班级异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 批量从班级移除学生
  Future<bool> removeStudentsFromClass(String classId, List<String> studentIds) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.removeStudentsFromClass(classId, studentIds);
      
      if (response.success) {
        // 更新班级学生数量
        final index = _classes.indexWhere((c) => c.id == classId);
        if (index != -1) {
          _classes[index] = _classes[index].copyWith(
            studentCount: _classes[index].studentCount - studentIds.length,
          );
          _applyFilters();
        }
        
        AppLogger.info('批量从班级移除学生成功: ${studentIds.length}名学生');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('批量从班级移除学生失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('批量从班级移除学生时发生错误');
      AppLogger.error('批量从班级移除学生异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 转移学生到其他班级
  Future<bool> transferStudent(String studentId, String fromClassId, String toClassId) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.transferStudent(studentId, fromClassId, toClassId);
      
      if (response.success) {
        // 更新两个班级的学生数量
        final fromIndex = _classes.indexWhere((c) => c.id == fromClassId);
        final toIndex = _classes.indexWhere((c) => c.id == toClassId);
        
        if (fromIndex != -1) {
          _classes[fromIndex] = _classes[fromIndex].copyWith(
            studentCount: _classes[fromIndex].studentCount - 1,
          );
        }
        
        if (toIndex != -1) {
          _classes[toIndex] = _classes[toIndex].copyWith(
            studentCount: _classes[toIndex].studentCount + 1,
          );
        }
        
        _applyFilters();
        AppLogger.info('学生转移成功');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('学生转移失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('转移学生时发生错误');
      AppLogger.error('转移学生异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 批量导入班级
  Future<bool> importClasses(String filePath) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.importClasses(
        filePath,
        grade: _selectedGrade,
      );
      
      if (response.success) {
        await loadClasses(forceRefresh: true); // 重新加载数据
        await loadStatistics(); // 刷新统计数据
        AppLogger.info('班级数据导入成功');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('班级数据导入失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('导入班级数据时发生错误');
      AppLogger.error('导入班级数据异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 导出班级数据
  Future<String?> exportClasses({String format = 'excel'}) async {
    if (_isLoading) return null;

    _setLoading(true);
    _clearError();

    try {
      final response = await _classRepository.exportClasses(
        grade: _selectedGrade,
        teacherId: _selectedTeacherId,
        format: format,
      );
      
      if (response.success && response.data != null) {
        AppLogger.info('班级数据导出成功: $format格式');
        return response.data!;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('班级数据导出失败: ${response.message}');
        return null;
      }
    } catch (e) {
      _setError('导出班级数据时发生错误');
      AppLogger.error('导出班级数据异常', e);
      return null;
    } finally {
      _setLoading(false);
    }
  }

  /// 搜索班级
  Future<List<ClassModel>?> searchClasses(String query, {String? grade, int limit = 10}) async {
    try {
      final response = await _classRepository.searchClasses(
        query,
        grade: grade,
        limit: limit,
      );
      
      if (response.success && response.data != null) {
        AppLogger.info('班级搜索成功: ${response.data!.length}个结果');
        return response.data!;
      } else {
        AppLogger.error('班级搜索失败: ${response.message}');
        return null;
      }
    } catch (e) {
      AppLogger.error('班级搜索异常', e);
      return null;
    }
  }

  /// 设置筛选条件
  void setFilters({
    String? grade,
    String? teacherId,
    bool? isActive,
  }) {
    _selectedGrade = grade;
    _selectedTeacherId = teacherId;
    _isActiveFilter = isActive;
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

  /// 设置选中的班级
  void setSelectedClass(ClassModel? classModel) {
    _selectedClass = classModel;
    notifyListeners();
  }

  /// 清除选中的班级
  void clearSelectedClass() {
    _selectedClass = null;
    notifyListeners();
  }

  /// 清除筛选条件
  void clearFilters() {
    _selectedGrade = null;
    _selectedTeacherId = null;
    _isActiveFilter = null;
    _searchQuery = '';
    _currentPage = 1;
    _applyFilters();
  }

  /// 刷新数据
  Future<void> refresh() async {
    await Future.wait([
      loadClasses(forceRefresh: true),
      loadStatistics(),
    ]);
  }

  /// 应用筛选
  void _applyFilters() {
    _filteredClasses = _classes.where((classData) {
      // 搜索筛选
      if (_searchQuery.isNotEmpty) {
        final query = _searchQuery.toLowerCase();
        if (!classData.name.toLowerCase().contains(query) &&
            !(classData.description?.toLowerCase().contains(query) ?? false) &&
            !(classData.teacherName?.toLowerCase().contains(query) ?? false) &&
            !classData.grade.toLowerCase().contains(query)) {
          return false;
        }
      }
      return true;
    }).toList();
    
    _applySorting();
  }

  /// 应用排序
  void _applySorting() {
    _filteredClasses.sort((a, b) {
      int comparison = 0;
      
      switch (_sortBy) {
        case 'name':
          comparison = a.name.compareTo(b.name);
          break;
        case 'grade':
          comparison = a.grade.compareTo(b.grade);
          break;
        case 'teacherName':
          comparison = (a.teacherName ?? '').compareTo(b.teacherName ?? '');
          break;
        case 'studentCount':
          comparison = a.studentCount.compareTo(b.studentCount);
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
    return _classes
        .map((classData) => classData.grade)
        .toSet()
        .toList()..sort();
  }

  /// 获取可用的教师列表
  List<String> get availableTeachers {
    return _classes
        .where((classData) => classData.teacherName != null)
        .map((classData) => classData.teacherName!)
        .toSet()
        .toList()..sort();
  }

  /// 获取指定年级的班级
  List<ClassModel> getClassesByGrade(String grade) {
    return _filteredClasses.where((classData) => classData.grade == grade).toList();
  }

  /// 获取指定教师的班级
  List<ClassModel> getClassesByTeacher(String teacherId) {
    return _filteredClasses.where((classData) => classData.teacherId == teacherId).toList();
  }

  /// 根据班级名称查找班级
  ClassModel? findClassByName(String className) {
    try {
      return _classes.firstWhere((classData) => classData.name == className);
    } catch (e) {
      return null;
    }
  }

  /// 根据班级名称搜索班级
  List<ClassModel> findClassesByName(String name) {
    final query = name.toLowerCase();
    return _classes.where((classData) => 
        classData.name.toLowerCase().contains(query)).toList();
  }

  /// 检查班级名称是否已存在
  bool isClassNameExists(String className, {String? excludeId}) {
    return _classes.any((classData) => 
        classData.name == className && classData.id != excludeId);
  }

  /// 获取班级总数
  int get totalClasses => _classes.length;

  /// 获取筛选后的班级数
  int get filteredClassesCount => _filteredClasses.length;

  /// 获取总学生数
  int get totalStudents => _classes.fold(0, (sum, classData) => sum + classData.studentCount);

  /// 获取激活的班级数
  int get activeClassesCount => _classes.where((c) => c.isActive).length;

  /// 获取停用的班级数
  int get inactiveClassesCount => _classes.where((c) => !c.isActive).length;

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
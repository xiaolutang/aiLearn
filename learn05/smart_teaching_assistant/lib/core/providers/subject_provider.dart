import 'package:flutter/foundation.dart';

import '../data/repositories/subject_repository.dart';
import '../services/connectivity_service.dart';
import '../utils/app_logger.dart';

/// 学科数据提供者
/// 负责管理学科相关的状态和业务逻辑
class SubjectProvider extends ChangeNotifier {
  final SubjectRepository _subjectRepository;
  final ConnectivityService _connectivityService;

  // 状态管理
  bool _isLoading = false;
  String? _error;
  List<Subject> _subjects = [];
  List<Subject> _filteredSubjects = [];
  SubjectStatistics? _statistics;
  Subject? _selectedSubject;

  // 筛选和分页
  int _currentPage = 1;
  int _pageSize = 20;
  String? _selectedCategory;
  String? _selectedGrade;
  String? _selectedTeacherId;
  String _searchQuery = '';
  String _sortBy = 'name';
  bool _sortAscending = true;
  bool? _isActiveFilter;

  SubjectProvider({
    required SubjectRepository subjectRepository,
    required ConnectivityService connectivityService,
  }) : _subjectRepository = subjectRepository,
       _connectivityService = connectivityService;

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<Subject> get subjects => _filteredSubjects;
  SubjectStatistics? get statistics => _statistics;
  Subject? get selectedSubject => _selectedSubject;
  int get currentPage => _currentPage;
  int get pageSize => _pageSize;
  String? get selectedCategory => _selectedCategory;
  String? get selectedGrade => _selectedGrade;
  String? get selectedTeacherId => _selectedTeacherId;
  String get searchQuery => _searchQuery;
  String get sortBy => _sortBy;
  bool get sortAscending => _sortAscending;
  bool? get isActiveFilter => _isActiveFilter;
  bool get hasError => _error != null;
  bool get isEmpty => _subjects.isEmpty && !_isLoading;
  bool get isNotEmpty => _subjects.isNotEmpty;

  // 获取可用的分类列表
  List<String> get availableCategories {
    final categories = _subjects
        .where((subject) => subject.category != null)
        .map((subject) => subject.category!)
        .toSet()
        .toList();
    categories.sort();
    return categories;
  }

  // 获取可用的年级列表
  List<String> get availableGrades {
    final grades = _subjects
        .where((subject) => subject.grade != null)
        .map((subject) => subject.grade!)
        .toSet()
        .toList();
    grades.sort();
    return grades;
  }

  // 获取可用的教师列表
  List<String> get availableTeachers {
    final teachers = _subjects
        .where((subject) => subject.teacherName != null)
        .map((subject) => subject.teacherName!)
        .toSet()
        .toList();
    teachers.sort();
    return teachers;
  }

  /// 加载学科列表
  Future<void> loadSubjects({
    bool forceRefresh = false,
    bool showLoading = true,
  }) async {
    if (showLoading) {
      _setLoading(true);
    }
    _clearError();

    try {
      final response = await _subjectRepository.getSubjects(
        category: _selectedCategory,
        grade: _selectedGrade,
        teacherId: _selectedTeacherId,
        searchQuery: _searchQuery.isNotEmpty ? _searchQuery : null,
        isActive: _isActiveFilter,
        page: _currentPage,
        pageSize: _pageSize,
        forceRefresh: forceRefresh,
      );

      if (response.success && response.data != null) {
        _subjects = response.data!.data;
        _applyFiltersAndSort();
      } else {
        _setError(response.message ?? '加载学科列表失败');
      }
    } catch (e) {
      AppLogger.error('SubjectProvider: 加载学科列表失败', e);
      _setError('加载学科列表失败: ${e.toString()}');
    } finally {
      if (showLoading) {
        _setLoading(false);
      }
    }
  }

  /// 加载学科统计数据
  Future<void> loadStatistics() async {
    try {
      final response = await _subjectRepository.getSubjectStatistics(
        category: _selectedCategory,
        grade: _selectedGrade,
      );

      if (response.success && response.data != null) {
        _statistics = response.data;
        notifyListeners();
      } else {
        AppLogger.warning('SubjectProvider: 加载学科统计失败: ${response.message}');
      }
    } catch (e) {
      AppLogger.error('SubjectProvider: 加载学科统计失败', e);
    }
  }

  /// 创建学科
  Future<bool> createSubject(Subject subject) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _subjectRepository.createSubject(subject.toJson());

      if (response.success && response.data != null) {
        await loadSubjects(showLoading: false);
        await loadStatistics();
        return true;
      } else {
        _setError(response.message ?? '创建学科失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('SubjectProvider: 创建学科失败', e);
      _setError('创建学科失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 更新学科
  Future<bool> updateSubject(Subject updatedSubject) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _subjectRepository.updateSubject(
        updatedSubject.id,
        updatedSubject.toJson(),
      );

      if (response.success && response.data != null) {
        await loadSubjects(showLoading: false);
        await loadStatistics();
        
        // 更新选中的学科
        if (_selectedSubject?.id == updatedSubject.id) {
          _selectedSubject = response.data;
        }
        
        return true;
      } else {
        _setError(response.message ?? '更新学科失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('SubjectProvider: 更新学科失败', e);
      _setError('更新学科失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 删除学科
  Future<bool> deleteSubject(String subjectId) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _subjectRepository.deleteSubject(subjectId);

      if (response.success) {
        await loadSubjects(showLoading: false);
        await loadStatistics();
        
        // 清除选中的学科
        if (_selectedSubject?.id == subjectId) {
          _selectedSubject = null;
        }
        
        return true;
      } else {
        _setError(response.message ?? '删除学科失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('SubjectProvider: 删除学科失败', e);
      _setError('删除学科失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 批量删除学科
  Future<bool> deleteSubjectsBatch(List<String> subjectIds) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _subjectRepository.deleteSubjectsBatch(subjectIds);

      if (response.success) {
        await loadSubjects(showLoading: false);
        await loadStatistics();
        
        // 清除选中的学科（如果在删除列表中）
        if (_selectedSubject != null && subjectIds.contains(_selectedSubject!.id)) {
          _selectedSubject = null;
        }
        
        return true;
      } else {
        _setError(response.message ?? '批量删除学科失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('SubjectProvider: 批量删除学科失败', e);
      _setError('批量删除学科失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 切换学科状态
  Future<bool> toggleSubjectStatus(String subjectId, bool isActive) async {
    try {
      final response = await _subjectRepository.toggleSubjectStatus(subjectId, isActive);

      if (response.success) {
        await loadSubjects(showLoading: false);
        await loadStatistics();
        return true;
      } else {
        _setError(response.message ?? '切换学科状态失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('SubjectProvider: 切换学科状态失败', e);
      _setError('切换学科状态失败: ${e.toString()}');
      return false;
    }
  }

  /// 导入学科数据
  Future<Map<String, dynamic>?> importSubjects(
    String filePath, {
    String? category,
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _subjectRepository.importSubjects(
        filePath,
        category: category,
      );

      if (response.success && response.data != null) {
        await loadSubjects(showLoading: false);
        await loadStatistics();
        return response.data;
      } else {
        _setError(response.message ?? '导入学科数据失败');
        return null;
      }
    } catch (e) {
      AppLogger.error('SubjectProvider: 导入学科数据失败', e);
      _setError('导入学科数据失败: ${e.toString()}');
      return null;
    } finally {
      _setLoading(false);
    }
  }

  /// 导出学科数据
  Future<String?> exportSubjects({
    String? category,
    String? grade,
    String format = 'excel',
  }) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _subjectRepository.exportSubjects(
        category: category,
        grade: grade,
        format: format,
      );

      if (response.success && response.data != null) {
        return response.data;
      } else {
        _setError(response.message ?? '导出学科数据失败');
        return null;
      }
    } catch (e) {
      AppLogger.error('SubjectProvider: 导出学科数据失败', e);
      _setError('导出学科数据失败: ${e.toString()}');
      return null;
    } finally {
      _setLoading(false);
    }
  }

  /// 搜索学科
  Future<List<Subject>> searchSubjects(
    String query, {
    String? category,
    String? grade,
    int limit = 10,
  }) async {
    try {
      final response = await _subjectRepository.searchSubjects(
        query,
        category: category,
        grade: grade,
        limit: limit,
      );

      if (response.success && response.data != null) {
        return response.data!;
      } else {
        AppLogger.warning('SubjectProvider: 搜索学科失败: ${response.message}');
        return [];
      }
    } catch (e) {
      AppLogger.error('SubjectProvider: 搜索学科失败', e);
      return [];
    }
  }

  /// 设置筛选条件
  void setFilters({
    String? category,
    String? grade,
    String? teacherId,
    bool? isActive,
  }) {
    bool hasChanged = false;
    
    if (_selectedCategory != category) {
      _selectedCategory = category;
      hasChanged = true;
    }
    
    if (_selectedGrade != grade) {
      _selectedGrade = grade;
      hasChanged = true;
    }
    
    if (_selectedTeacherId != teacherId) {
      _selectedTeacherId = teacherId;
      hasChanged = true;
    }
    
    if (_isActiveFilter != isActive) {
      _isActiveFilter = isActive;
      hasChanged = true;
    }
    
    if (hasChanged) {
      _currentPage = 1; // 重置到第一页
      loadSubjects();
    }
  }

  /// 设置搜索查询
  void setSearchQuery(String query) {
    if (_searchQuery != query) {
      _searchQuery = query;
      _currentPage = 1; // 重置到第一页
      _applyFiltersAndSort();
      notifyListeners();
    }
  }

  /// 设置排序
  void setSorting(String sortBy, {bool? ascending}) {
    bool hasChanged = false;
    
    if (_sortBy != sortBy) {
      _sortBy = sortBy;
      hasChanged = true;
    }
    
    if (ascending != null && _sortAscending != ascending) {
      _sortAscending = ascending;
      hasChanged = true;
    } else if (ascending == null && _sortBy == sortBy) {
      // 如果点击相同的列，切换排序方向
      _sortAscending = !_sortAscending;
      hasChanged = true;
    }
    
    if (hasChanged) {
      _applyFiltersAndSort();
      notifyListeners();
    }
  }

  /// 设置分页
  void setPage(int page) {
    if (_currentPage != page) {
      _currentPage = page;
      loadSubjects();
    }
  }

  /// 设置页面大小
  void setPageSize(int pageSize) {
    if (_pageSize != pageSize) {
      _pageSize = pageSize;
      _currentPage = 1; // 重置到第一页
      loadSubjects();
    }
  }

  /// 设置选中的学科
  void setSelectedSubject(Subject? subject) {
    if (_selectedSubject != subject) {
      _selectedSubject = subject;
      notifyListeners();
    }
  }

  /// 清除选中的学科
  void clearSelectedSubject() {
    setSelectedSubject(null);
  }

  /// 清除所有筛选条件
  void clearFilters() {
    _selectedCategory = null;
    _selectedGrade = null;
    _selectedTeacherId = null;
    _isActiveFilter = null;
    _searchQuery = '';
    _currentPage = 1;
    loadSubjects();
  }

  /// 刷新数据
  Future<void> refresh() async {
    await loadSubjects(forceRefresh: true);
    await loadStatistics();
  }

  /// 应用筛选和排序
  void _applyFiltersAndSort() {
    var filtered = List<Subject>.from(_subjects);
    
    // 应用搜索筛选
    if (_searchQuery.isNotEmpty) {
      final query = _searchQuery.toLowerCase();
      filtered = filtered.where((subject) {
        return subject.name.toLowerCase().contains(query) ||
               subject.code.toLowerCase().contains(query) ||
               (subject.description?.toLowerCase().contains(query) ?? false) ||
               (subject.category?.toLowerCase().contains(query) ?? false);
      }).toList();
    }
    
    // 排序
    _sortSubjects(filtered);
    
    _filteredSubjects = filtered;
  }

  /// 排序学科列表
  void _sortSubjects(List<Subject> subjects) {
    subjects.sort((a, b) {
      int comparison = 0;
      
      switch (_sortBy) {
        case 'name':
          comparison = a.name.compareTo(b.name);
          break;
        case 'code':
          comparison = a.code.compareTo(b.code);
          break;
        case 'category':
          comparison = (a.category ?? '').compareTo(b.category ?? '');
          break;
        case 'grade':
          comparison = (a.grade ?? '').compareTo(b.grade ?? '');
          break;
        case 'creditHours':
          comparison = (a.creditHours ?? 0).compareTo(b.creditHours ?? 0);
          break;
        case 'teacherName':
          comparison = (a.teacherName ?? '').compareTo(b.teacherName ?? '');
          break;
        case 'createdAt':
          comparison = a.createdAt.compareTo(b.createdAt);
          break;
        case 'isActive':
          comparison = a.isActive.toString().compareTo(b.isActive.toString());
          break;
        default:
          comparison = a.name.compareTo(b.name);
      }
      
      return _sortAscending ? comparison : -comparison;
    });
  }

  /// 设置加载状态
  void _setLoading(bool loading) {
    if (_isLoading != loading) {
      _isLoading = loading;
      notifyListeners();
    }
  }

  /// 设置错误信息
  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  /// 清除错误信息
  void _clearError() {
    if (_error != null) {
      _error = null;
      notifyListeners();
    }
  }

  /// 重置状态
  void reset() {
    _isLoading = false;
    _error = null;
    _subjects.clear();
    _filteredSubjects.clear();
    _statistics = null;
    _selectedSubject = null;
    _currentPage = 1;
    _selectedCategory = null;
    _selectedGrade = null;
    _selectedTeacherId = null;
    _searchQuery = '';
    _sortBy = 'name';
    _sortAscending = true;
    _isActiveFilter = null;
    notifyListeners();
  }

  @override
  void dispose() {
    reset();
    super.dispose();
  }
}
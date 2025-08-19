import 'package:flutter/foundation.dart';

import '../data/repositories/grade_repository.dart';
import '../services/connectivity_service.dart';
import '../utils/app_logger.dart';
import '../models/grade_model.dart';

/// 成绩数据提供者
/// 负责管理成绩相关的状态和业务逻辑
class GradeProvider extends ChangeNotifier {
  final GradeRepository _gradeRepository;
  final ConnectivityService _connectivityService;

  // 状态管理
  bool _isLoading = false;
  String? _error;
  List<Grade> _grades = [];
  List<Grade> _filteredGrades = [];
  GradeStatistics? _statistics;

  // 筛选和分页
  int _currentPage = 1;
  int _pageSize = 20;
  String? _selectedClassId;
  String? _selectedSubjectId;
  String? _selectedExamId;
  DateTime? _startDate;
  DateTime? _endDate;
  String _searchQuery = '';
  String _sortBy = 'examDate';
  bool _sortAscending = false;

  GradeProvider({
    required GradeRepository gradeRepository,
    required ConnectivityService connectivityService,
  }) : _gradeRepository = gradeRepository,
       _connectivityService = connectivityService;

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<Grade> get grades => _filteredGrades;
  GradeStatistics? get statistics => _statistics;
  int get currentPage => _currentPage;
  int get pageSize => _pageSize;
  String? get selectedClassId => _selectedClassId;
  String? get selectedSubjectId => _selectedSubjectId;
  String? get selectedExamId => _selectedExamId;
  DateTime? get startDate => _startDate;
  DateTime? get endDate => _endDate;
  String get searchQuery => _searchQuery;
  String get sortBy => _sortBy;
  bool get sortAscending => _sortAscending;
  bool get hasError => _error != null;
  bool get isEmpty => _grades.isEmpty && !_isLoading;
  bool get isNotEmpty => _grades.isNotEmpty;
  bool get hasMore => _grades.length >= _pageSize; // 简单的分页判断

  /// 加载成绩数据
  Future<void> loadGrades({bool forceRefresh = false}) async {
    if (_isLoading) return;

    _setLoading(true);
    _clearError();

    try {
      final response = await _gradeRepository.getGrades(
        page: _currentPage,
        pageSize: _pageSize,
        classId: _selectedClassId,
        subjectId: _selectedSubjectId,
        examType: _selectedExamId,
        startDate: _startDate,
        endDate: _endDate,
        forceRefresh: forceRefresh,
      );

      if (response.success && response.data != null) {
        _grades = response.data!.items;
        _applyFilters();
        AppLogger.info('成绩数据加载成功: ${_grades.length}条记录');
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('成绩数据加载失败: ${response.message}');
      }
    } catch (e) {
      _setError('加载成绩数据时发生错误');
      AppLogger.error('加载成绩数据异常', e);
    } finally {
      _setLoading(false);
    }
  }

  /// 加载成绩统计数据
  Future<void> loadStatistics({bool forceRefresh = false}) async {
    try {
      final response = await _gradeRepository.getGradeStatistics(
        classId: _selectedClassId,
        subjectId: _selectedSubjectId,
        startDate: _startDate,
        endDate: _endDate,
      );

      if (response.success && response.data != null) {
        _statistics = response.data!;
        notifyListeners();
        AppLogger.info('成绩统计数据加载成功');
      } else {
        AppLogger.error('成绩统计数据加载失败: ${response.message}');
      }
    } catch (e) {
      AppLogger.error('加载成绩统计数据异常', e);
    }
  }

  /// 创建成绩记录
  Future<bool> createGrade(Grade grade) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _gradeRepository.createGrade(grade.toJson());
      
      if (response.success && response.data != null) {
        _grades.add(response.data!);
        _applyFilters();
        await loadStatistics(); // 刷新统计数据
        AppLogger.info('成绩记录创建成功: ${grade.studentName} - ${grade.subjectName}');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('成绩记录创建失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('创建成绩记录时发生错误');
      AppLogger.error('创建成绩记录异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 更新成绩记录
  Future<bool> updateGrade(String gradeId, Grade updatedGrade) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _gradeRepository.updateGrade(gradeId, updatedGrade.toJson());
      
      if (response.success && response.data != null) {
        final index = _grades.indexWhere((g) => g.id == gradeId);
        if (index != -1) {
          _grades[index] = response.data!;
          _applyFilters();
          await loadStatistics(); // 刷新统计数据
          AppLogger.info('成绩记录更新成功: ${updatedGrade.studentName}');
          return true;
        }
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('成绩记录更新失败: ${response.message}');
      }
      return false;
    } catch (e) {
      _setError('更新成绩记录时发生错误');
      AppLogger.error('更新成绩记录异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 删除成绩记录
  Future<bool> deleteGrade(String gradeId) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _gradeRepository.deleteGrade(gradeId);
      
      if (response.success) {
        _grades.removeWhere((g) => g.id == gradeId);
        _applyFilters();
        await loadStatistics(); // 刷新统计数据
        AppLogger.info('成绩记录删除成功');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('成绩记录删除失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('删除成绩记录时发生错误');
      AppLogger.error('删除成绩记录异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 批量导入成绩
  Future<bool> importGrades(String filePath) async {
    if (_isLoading) return false;

    _setLoading(true);
    _clearError();

    try {
      final response = await _gradeRepository.importGrades(
        filePath,
        classId: _selectedClassId,
        examType: _selectedExamId,
      );
      
      if (response.success) {
        await loadGrades(forceRefresh: true); // 重新加载数据
        await loadStatistics(forceRefresh: true);
        AppLogger.info('成绩数据导入成功');
        return true;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('成绩数据导入失败: ${response.message}');
        return false;
      }
    } catch (e) {
      _setError('导入成绩数据时发生错误');
      AppLogger.error('导入成绩数据异常', e);
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 导出成绩数据
  Future<String?> exportGrades({String format = 'excel'}) async {
    if (_isLoading) return null;

    _setLoading(true);
    _clearError();

    try {
      final response = await _gradeRepository.exportGrades(
        classId: _selectedClassId,
        subjectId: _selectedSubjectId,
        startDate: _startDate,
        endDate: _endDate,
        format: format,
      );
      
      if (response.success && response.data != null) {
        AppLogger.info('成绩数据导出成功: $format格式');
        return response.data!;
      } else {
        _setError(response.userFriendlyMessage);
        AppLogger.error('成绩数据导出失败: ${response.message}');
        return null;
      }
    } catch (e) {
      _setError('导出成绩数据时发生错误');
      AppLogger.error('导出成绩数据异常', e);
      return null;
    } finally {
      _setLoading(false);
    }
  }

  /// 设置筛选条件
  void setFilters({
    String? classId,
    String? subjectId,
    String? examId,
    DateTime? startDate,
    DateTime? endDate,
  }) {
    _selectedClassId = classId;
    _selectedSubjectId = subjectId;
    _selectedExamId = examId;
    _startDate = startDate;
    _endDate = endDate;
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
      _sortAscending = _sortBy == sortBy ? !_sortAscending : false;
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
    _selectedSubjectId = null;
    _selectedExamId = null;
    _startDate = null;
    _endDate = null;
    _searchQuery = '';
    _currentPage = 1;
    _applyFilters();
  }

  /// 刷新数据
  Future<void> refresh() async {
    await Future.wait([
      loadGrades(forceRefresh: true),
      loadStatistics(forceRefresh: true),
    ]);
  }

  /// 应用筛选
  void _applyFilters() {
    _filteredGrades = _grades.where((grade) {
      // 搜索筛选
      if (_searchQuery.isNotEmpty && 
          !grade.studentName.toLowerCase().contains(_searchQuery.toLowerCase())) {
        return false;
      }
      return true;
    }).toList();
    
    _applySorting();
  }

  /// 应用排序
  void _applySorting() {
    _filteredGrades.sort((a, b) {
      int comparison = 0;
      
      switch (_sortBy) {
        case 'studentName':
          comparison = a.studentName.compareTo(b.studentName);
          break;
        case 'subjectName':
          comparison = a.subjectName.compareTo(b.subjectName);
          break;
        case 'score':
          comparison = a.score.compareTo(b.score);
          break;
        case 'examDate':
          comparison = a.examDate.compareTo(b.examDate);
          break;
        case 'examName':
          comparison = a.examName.compareTo(b.examName);
          break;
        default:
          comparison = a.examDate.compareTo(b.examDate);
      }
      
      return _sortAscending ? comparison : -comparison;
    });
    
    notifyListeners();
  }

  /// 获取可用的科目列表
  List<String> get availableSubjects {
    return _grades
        .map((grade) => grade.subjectName)
        .toSet()
        .toList();
  }

  /// 获取可用的考试类型列表
  List<String> get availableExamIds {
    return _grades
        .map((grade) => grade.examName)
        .toSet()
        .toList();
  }

  /// 获取指定学生的成绩
  List<Grade> getGradesByStudent(String studentId) {
    return _filteredGrades.where((grade) => grade.studentId == studentId).toList();
  }

  /// 获取指定科目的成绩
  List<Grade> getGradesBySubject(String subjectId) {
    return _filteredGrades.where((grade) => grade.subjectId == subjectId).toList();
  }

  /// 获取指定考试的成绩
  List<Grade> getGradesByExam(String examId) {
    return _filteredGrades.where((grade) => grade.examId == examId).toList();
  }

  /// 计算平均分
  double get averageScore {
    if (_filteredGrades.isEmpty) return 0.0;
    final total = _filteredGrades.fold<double>(0.0, (sum, grade) => sum + grade.score);
    return total / _filteredGrades.length;
  }

  /// 获取最高分
  double get highestScore {
    if (_filteredGrades.isEmpty) return 0.0;
    return _filteredGrades.map((grade) => grade.score).reduce((a, b) => a > b ? a : b);
  }

  /// 获取最低分
  double get lowestScore {
    if (_filteredGrades.isEmpty) return 0.0;
    return _filteredGrades.map((grade) => grade.score).reduce((a, b) => a < b ? a : b);
  }

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

  /// 公开的清除错误方法
  void clearError() {
    _clearError();
  }

  /// 加载更多成绩数据
  Future<void> loadMoreGrades() async {
    if (_isLoading || !hasMore) return;
    
    _currentPage++;
    await loadGrades();
  }

  /// 加载考试列表（暂时返回空，后续可扩展）
  Future<void> loadExams({bool refresh = false}) async {
    // 暂时空实现，后续可以添加考试数据加载逻辑
    AppLogger.info('加载考试列表');
  }

  /// 加载科目列表（暂时返回空，后续可扩展）
  Future<void> loadSubjects({bool refresh = false}) async {
    // 暂时空实现，后续可以添加科目数据加载逻辑
    AppLogger.info('加载科目列表');
  }

  @override
  void dispose() {
    super.dispose();
  }
}
import 'package:flutter/foundation.dart';

import '../data/repositories/tutoring_repository.dart';
import '../models/tutoring_model.dart';
import '../services/connectivity_service.dart';
import '../utils/app_logger.dart';

// 导入TutoringSolution类
export '../data/repositories/tutoring_repository.dart' show TutoringSolution, TutoringRequest, TutoringHistory, TutoringStatistics;

/// AI辅导数据提供者
/// 负责管理AI辅导相关的状态和业务逻辑
class TutoringProvider extends ChangeNotifier {
  final TutoringRepository _tutoringRepository;
  final ConnectivityService _connectivityService;

  // 状态管理
  bool _isLoading = false;
  String? _error;
  List<TutoringSolution> _solutions = [];
  List<TutoringSolution> _filteredSolutions = [];
  TutoringSolution? _selectedSolution;
  TutoringStatistics? _statistics;

  // 筛选和分页
  int _currentPage = 1;
  int _pageSize = 20;
  String? _selectedStudentId;
  String? _selectedSubjectId;
  String? _selectedDifficulty;
  String? _selectedType;
  String _searchQuery = '';
  String _sortBy = 'createdAt';
  bool _sortAscending = false;
  DateTime? _startDate;
  DateTime? _endDate;

  // AI辅导会话状态
  bool _isGenerating = false;
  String? _currentSessionId;
  List<TutoringMessage> _currentMessages = [];

  TutoringProvider({
    required TutoringRepository tutoringRepository,
    required ConnectivityService connectivityService,
  }) : _tutoringRepository = tutoringRepository,
       _connectivityService = connectivityService;

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<TutoringSolution> get solutions => _filteredSolutions;
  TutoringSolution? get selectedSolution => _selectedSolution;
  TutoringStatistics? get statistics => _statistics;
  int get currentPage => _currentPage;
  int get pageSize => _pageSize;
  String? get selectedStudentId => _selectedStudentId;
  String? get selectedSubjectId => _selectedSubjectId;
  String? get selectedDifficulty => _selectedDifficulty;
  String? get selectedType => _selectedType;
  String get searchQuery => _searchQuery;
  String get sortBy => _sortBy;
  bool get sortAscending => _sortAscending;
  DateTime? get startDate => _startDate;
  DateTime? get endDate => _endDate;
  bool get hasError => _error != null;
  bool get isEmpty => _solutions.isEmpty && !_isLoading;
  bool get isNotEmpty => _solutions.isNotEmpty;

  // AI辅导会话相关
  bool get isGenerating => _isGenerating;
  String? get currentSessionId => _currentSessionId;
  List<TutoringMessage> get currentMessages => _currentMessages;
  bool get hasActiveSession => _currentSessionId != null;

  // 获取可用的难度级别列表
  List<String> get availableDifficulties {
    final difficulties = _solutions
        .where((solution) => solution.difficulty != null)
        .map((solution) => solution.difficulty!)
        .toSet()
        .toList();
    difficulties.sort();
    return difficulties;
  }

  // 获取可用的辅导类型列表
  List<String> get availableTypes {
    final types = _solutions
        .where((solution) => solution.type != null)
        .map((solution) => solution.type!)
        .toSet()
        .toList();
    types.sort();
    return types;
  }

  // 获取可用的学科列表
  List<String> get availableSubjects {
    final subjects = _solutions
        .where((solution) => solution.subjectName != null)
        .map((solution) => solution.subjectName!)
        .toSet()
        .toList();
    subjects.sort();
    return subjects;
  }

  /// 加载辅导方案列表
  Future<void> loadSolutions({
    bool forceRefresh = false,
    bool showLoading = true,
  }) async {
    if (showLoading) {
      _setLoading(true);
    }
    _clearError();

    try {
      final response = await _tutoringRepository.getSolutions();

      if (response.success && response.data != null) {
        _solutions = response.data!;
        _applyFiltersAndSort();
      } else {
        _setError(response.message ?? '加载辅导方案失败');
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 加载辅导方案失败', e);
      _setError('加载辅导方案失败: ${e.toString()}');
    } finally {
      if (showLoading) {
        _setLoading(false);
      }
    }
  }

  /// 加载辅导统计数据
  Future<void> loadStatistics() async {
    try {
      final response = await _tutoringRepository.getTutoringStatistics();

      if (response.success && response.data != null) {
        _statistics = response.data;
        notifyListeners();
      } else {
        AppLogger.warning('TutoringProvider: 加载辅导统计失败: ${response.message}');
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 加载辅导统计失败', e);
    }
  }

  /// 根据ID获取辅导方案
  Future<TutoringSolution?> getSolutionById(String solutionId) async {
    try {
      final response = await _tutoringRepository.getTutoringSolution(solutionId);

      if (response.success && response.data != null) {
        return response.data;
      } else {
        AppLogger.warning('TutoringProvider: 获取辅导方案失败: ${response.message}');
        return null;
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 获取辅导方案失败', e);
      return null;
    }
  }

  /// 生成AI辅导方案
  Future<TutoringSolution?> generateSolution({
    required String studentId,
    required String subjectId,
    required String problemDescription,
    String? difficulty,
    String? type,
    Map<String, dynamic>? additionalContext,
  }) async {
    _setGenerating(true);
    _clearError();

    try {
      final response = await _tutoringRepository.generateSolution(
        studentId: studentId,
        subjectId: subjectId,
        problemDescription: problemDescription,
        difficulty: difficulty,
        type: type,
        additionalContext: additionalContext,
      );

      if (response.success && response.data != null) {
        await loadSolutions(showLoading: false);
        await loadStatistics();
        return response.data;
      } else {
        _setError(response.message ?? '生成辅导方案失败');
        return null;
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 生成辅导方案失败', e);
      _setError('生成辅导方案失败: ${e.toString()}');
      return null;
    } finally {
      _setGenerating(false);
    }
  }

  /// 创建辅导方案
  Future<bool> createSolution(TutoringSolution solution) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _tutoringRepository.createSolution(solution.toJson());

      if (response.success && response.data != null) {
        await loadSolutions(showLoading: false);
        await loadStatistics();
        return true;
      } else {
        _setError(response.message ?? '创建辅导方案失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 创建辅导方案失败', e);
      _setError('创建辅导方案失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 更新辅导方案
  Future<bool> updateSolution(TutoringSolution updatedSolution) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _tutoringRepository.updateSolution(
        updatedSolution.id,
        updatedSolution.toJson(),
      );

      if (response.success && response.data != null) {
        await loadSolutions(showLoading: false);
        await loadStatistics();
        
        // 更新选中的方案
        if (_selectedSolution?.id == updatedSolution.id) {
          _selectedSolution = response.data;
        }
        
        return true;
      } else {
        _setError(response.message ?? '更新辅导方案失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 更新辅导方案失败', e);
      _setError('更新辅导方案失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 删除辅导方案
  Future<bool> deleteSolution(String solutionId) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _tutoringRepository.deleteSolution(solutionId);

      if (response.success) {
        await loadSolutions(showLoading: false);
        await loadStatistics();
        
        // 清除选中的方案
        if (_selectedSolution?.id == solutionId) {
          _selectedSolution = null;
        }
        
        return true;
      } else {
        _setError(response.message ?? '删除辅导方案失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 删除辅导方案失败', e);
      _setError('删除辅导方案失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 批量删除辅导方案
  Future<bool> deleteSolutionsBatch(List<String> solutionIds) async {
    _setLoading(true);
    _clearError();

    try {
      final response = await _tutoringRepository.deleteSolutionsBatch(solutionIds);

      if (response.success) {
        await loadSolutions(showLoading: false);
        await loadStatistics();
        
        // 清除选中的方案（如果在删除列表中）
        if (_selectedSolution != null && solutionIds.contains(_selectedSolution!.id)) {
          _selectedSolution = null;
        }
        
        return true;
      } else {
        _setError(response.message ?? '批量删除辅导方案失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 批量删除辅导方案失败', e);
      _setError('批量删除辅导方案失败: ${e.toString()}');
      return false;
    } finally {
      _setLoading(false);
    }
  }

  /// 评价辅导方案
  Future<bool> rateSolution(
    String solutionId,
    int rating, {
    String? feedback,
  }) async {
    try {
      final response = await _tutoringRepository.rateSolution(
        solutionId,
        rating,
      );

      if (response.success && response.data != null) {
        await loadSolutions(showLoading: false);
        
        // 更新选中的方案
        if (_selectedSolution?.id == solutionId) {
          _selectedSolution = response.data;
          notifyListeners();
        }
        
        return true;
      } else {
        _setError(response.message ?? '评价辅导方案失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 评价辅导方案失败', e);
      _setError('评价辅导方案失败: ${e.toString()}');
      return false;
    }
  }

  /// 开始AI辅导会话
  Future<String?> startTutoringSession({
    required String studentId,
    required String subjectId,
    String? problemDescription,
    Map<String, dynamic>? context,
  }) async {
    _setGenerating(true);
    _clearError();

    try {
      final response = await _tutoringRepository.startTutoringSession(
        studentId: studentId,
        subjectId: subjectId,
        problemDescription: problemDescription,
        context: context,
      );

      if (response.success && response.data != null) {
        _currentSessionId = response.data!;
        _currentMessages = [];
        notifyListeners();
        return _currentSessionId;
      } else {
        _setError(response.message ?? '开始辅导会话失败');
        return null;
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 开始辅导会话失败', e);
      _setError('开始辅导会话失败: ${e.toString()}');
      return null;
    } finally {
      _setGenerating(false);
    }
  }

  /// 发送消息到AI辅导会话
  Future<bool> sendMessage(
    String sessionId,
    String message, {
    Map<String, dynamic>? attachments,
  }) async {
    if (_currentSessionId != sessionId) {
      _setError('会话ID不匹配');
      return false;
    }

    _setGenerating(true);
    _clearError();

    try {
      final response = await _tutoringRepository.sendMessage(
        sessionId,
        message,
      );

      if (response.success && response.data != null) {
        _currentMessages = (response.data!['messages'] as List<dynamic>? ?? [])
            .map((msg) => TutoringMessage.fromJson(msg))
            .toList();
        notifyListeners();
        return true;
      } else {
        _setError(response.message ?? '发送消息失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 发送消息失败', e);
      _setError('发送消息失败: ${e.toString()}');
      return false;
    } finally {
      _setGenerating(false);
    }
  }

  /// 结束AI辅导会话
  Future<bool> endTutoringSession(String sessionId) async {
    try {
      final response = await _tutoringRepository.endSession(sessionId);

      if (response.success) {
        _currentSessionId = null;
        _currentMessages.clear();
        notifyListeners();
        return true;
      } else {
        _setError(response.message ?? '结束辅导会话失败');
        return false;
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 结束辅导会话失败', e);
      _setError('结束辅导会话失败: ${e.toString()}');
      return false;
    }
  }

  /// 获取辅导会话历史
  Future<List<TutoringMessage>> getSessionHistory(String sessionId) async {
    try {
      final response = await _tutoringRepository.getSessionHistory(sessionId);

      if (response.success && response.data != null) {
        return (response.data! as List<dynamic>)
            .map((msg) => TutoringMessage.fromJson(msg))
            .toList();
      } else {
        AppLogger.warning('TutoringProvider: 获取会话历史失败: ${response.message}');
        return [];
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 获取会话历史失败', e);
      return [];
    }
  }

  /// 搜索辅导方案
  Future<List<TutoringSolution>> searchSolutions(
    String query, {
    String? studentId,
    String? subjectId,
    String? difficulty,
    int limit = 10,
  }) async {
    try {
      final response = await _tutoringRepository.searchTutoringSolutions(
        query,
        subject: subjectId,
        difficulty: difficulty,
        limit: limit,
      );

      if (response.success && response.data != null) {
        return response.data!;
      } else {
        AppLogger.warning('TutoringProvider: 搜索辅导方案失败: ${response.message}');
        return [];
      }
    } catch (e) {
      AppLogger.error('TutoringProvider: 搜索辅导方案失败', e);
      return [];
    }
  }

  /// 设置筛选条件
  void setFilters({
    String? studentId,
    String? subjectId,
    String? difficulty,
    String? type,
    DateTime? startDate,
    DateTime? endDate,
  }) {
    bool hasChanged = false;
    
    if (_selectedStudentId != studentId) {
      _selectedStudentId = studentId;
      hasChanged = true;
    }
    
    if (_selectedSubjectId != subjectId) {
      _selectedSubjectId = subjectId;
      hasChanged = true;
    }
    
    if (_selectedDifficulty != difficulty) {
      _selectedDifficulty = difficulty;
      hasChanged = true;
    }
    
    if (_selectedType != type) {
      _selectedType = type;
      hasChanged = true;
    }
    
    if (_startDate != startDate) {
      _startDate = startDate;
      hasChanged = true;
    }
    
    if (_endDate != endDate) {
      _endDate = endDate;
      hasChanged = true;
    }
    
    if (hasChanged) {
      _currentPage = 1; // 重置到第一页
      loadSolutions();
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
      loadSolutions();
    }
  }

  /// 设置页面大小
  void setPageSize(int pageSize) {
    if (_pageSize != pageSize) {
      _pageSize = pageSize;
      _currentPage = 1; // 重置到第一页
      loadSolutions();
    }
  }

  /// 设置选中的辅导方案
  void setSelectedSolution(TutoringSolution? solution) {
    if (_selectedSolution != solution) {
      _selectedSolution = solution;
      notifyListeners();
    }
  }

  /// 清除选中的辅导方案
  void clearSelectedSolution() {
    setSelectedSolution(null);
  }

  /// 清除所有筛选条件
  void clearFilters() {
    _selectedStudentId = null;
    _selectedSubjectId = null;
    _selectedDifficulty = null;
    _selectedType = null;
    _startDate = null;
    _endDate = null;
    _searchQuery = '';
    _currentPage = 1;
    loadSolutions();
  }

  /// 刷新数据
  Future<void> refresh() async {
    await loadSolutions(forceRefresh: true);
    await loadStatistics();
  }

  /// 应用筛选和排序
  void _applyFiltersAndSort() {
    var filtered = List<TutoringSolution>.from(_solutions);
    
    // 应用搜索筛选
    if (_searchQuery.isNotEmpty) {
      final query = _searchQuery.toLowerCase();
      filtered = filtered.where((solution) {
        return (solution.title?.toLowerCase().contains(query) ?? false) ||
               (solution.description?.toLowerCase().contains(query) ?? false) ||
               (solution.subjectName?.toLowerCase().contains(query) ?? false) ||
               (solution.type?.toLowerCase().contains(query) ?? false) ||
               (solution.difficulty?.toLowerCase().contains(query) ?? false);
      }).toList();
    }
    
    // 排序
    _sortSolutions(filtered);
    
    _filteredSolutions = filtered;
  }

  /// 排序辅导方案列表
  void _sortSolutions(List<TutoringSolution> solutions) {
    solutions.sort((a, b) {
      int comparison = 0;
      
      switch (_sortBy) {
        case 'title':
          comparison = (a.title ?? '').compareTo(b.title ?? '');
          break;
        case 'subjectName':
          comparison = (a.subjectName ?? '').compareTo(b.subjectName ?? '');
          break;
        case 'type':
          comparison = (a.type ?? '').compareTo(b.type ?? '');
          break;
        case 'difficulty':
          comparison = (a.difficulty ?? '').compareTo(b.difficulty ?? '');
          break;
        case 'rating':
          comparison = (a.rating ?? 0.0).compareTo(b.rating ?? 0.0);
          break;
        case 'createdAt':
          comparison = a.createdAt.compareTo(b.createdAt);
          break;
        case 'updatedAt':
          comparison = (a.updatedAt ?? DateTime.now()).compareTo(b.updatedAt ?? DateTime.now());
          break;
        default:
          comparison = a.createdAt.compareTo(b.createdAt);
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

  /// 设置生成状态
  void _setGenerating(bool generating) {
    if (_isGenerating != generating) {
      _isGenerating = generating;
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
    _isGenerating = false;
    _error = null;
    _solutions.clear();
    _filteredSolutions.clear();
    _selectedSolution = null;
    _statistics = null;
    _currentPage = 1;
    _selectedStudentId = null;
    _selectedSubjectId = null;
    _selectedDifficulty = null;
    _selectedType = null;
    _startDate = null;
    _endDate = null;
    _searchQuery = '';
    _sortBy = 'createdAt';
    _sortAscending = false;
    _currentSessionId = null;
    _currentMessages.clear();
    notifyListeners();
  }

  @override
  void dispose() {
    reset();
    super.dispose();
  }
}
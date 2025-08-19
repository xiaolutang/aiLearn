import '../utils/api_client.dart';
import '../utils/constants.dart';

class TutoringService {
  final ApiClient _apiClient;
  
  TutoringService(this._apiClient);
  
  /// 生成辅导方案
  Future<Map<String, dynamic>> generateTutoringPlan({
    required String studentId,
    String? subjectId,
    String? examId,
    List<String>? weaknessAreas,
    String? difficultyLevel,
    int? duration, // 辅导时长（天）
  }) async {
    final data = <String, dynamic>{
      'studentId': studentId,
    };
    if (subjectId != null) data['subjectId'] = subjectId;
    if (examId != null) data['examId'] = examId;
    if (weaknessAreas != null) data['weaknessAreas'] = weaknessAreas;
    if (difficultyLevel != null) data['difficultyLevel'] = difficultyLevel;
    if (duration != null) data['duration'] = duration;
    
    final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/tutoring/generate',
      data: data,
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '生成辅导方案失败');
    }
  }
  
  /// 获取辅导方案列表
  Future<Map<String, dynamic>> getTutoringPlans({
    String? studentId,
    String? status,
    int page = 1,
    int pageSize = 20,
  }) async {
    final queryParams = <String, dynamic>{
      'page': page.toString(),
      'pageSize': pageSize.toString(),
    };
    if (studentId != null) queryParams['studentId'] = studentId;
    if (status != null) queryParams['status'] = status;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/tutoring/plans').replace(
      queryParameters: queryParams
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取辅导方案列表失败');
    }
  }
  
  /// 获取辅导方案详情
  Future<Map<String, dynamic>> getTutoringPlanDetail(String planId) async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/tutoring/plans/$planId',
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取辅导方案详情失败');
    }
  }
  
  /// 更新辅导方案
  Future<bool> updateTutoringPlan({
    required String planId,
    String? title,
    String? description,
    List<Map<String, dynamic>>? tasks,
    String? status,
  }) async {
    final data = <String, dynamic>{};
    if (title != null) data['title'] = title;
    if (description != null) data['description'] = description;
    if (tasks != null) data['tasks'] = tasks;
    if (status != null) data['status'] = status;
    
    final response = await _apiClient.put<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/tutoring/plans/$planId',
      data: data,
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success) {
      return true;
    } else {
      throw Exception(response.message ?? '更新辅导方案失败');
    }
  }
  
  /// 删除辅导方案
  Future<bool> deleteTutoringPlan(String planId) async {
    final response = await _apiClient.delete<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/tutoring/plans/$planId',
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success) {
      return true;
    } else {
      throw Exception(response.message ?? '删除辅导方案失败');
    }
  }
  
  /// 获取练习题推荐
  Future<Map<String, dynamic>> getExerciseRecommendations({
    required String studentId,
    String? subjectId,
    List<String>? knowledgePoints,
    String? difficultyLevel,
    int? count,
  }) async {
    final queryParams = <String, dynamic>{
      'studentId': studentId,
    };
    if (subjectId != null) queryParams['subjectId'] = subjectId;
    if (knowledgePoints != null) queryParams['knowledgePoints'] = knowledgePoints.join(',');
    if (difficultyLevel != null) queryParams['difficultyLevel'] = difficultyLevel;
    if (count != null) queryParams['count'] = count.toString();
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/tutoring/exercises/recommendations').replace(
      queryParameters: queryParams
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取练习题推荐失败');
    }
  }
  
  /// 提交练习结果
  Future<bool> submitExerciseResult({
    required String exerciseId,
    required String studentId,
    required Map<String, dynamic> answers,
    int? timeSpent, // 用时（秒）
  }) async {
    final data = <String, dynamic>{
      'exerciseId': exerciseId,
      'studentId': studentId,
      'answers': answers,
    };
    if (timeSpent != null) data['timeSpent'] = timeSpent;
    
    final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/tutoring/exercises/submit',
      data: data,
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success) {
      return true;
    } else {
      throw Exception(response.message ?? '提交练习结果失败');
    }
  }
  
  /// 获取学习建议
  Future<Map<String, dynamic>> getLearningRecommendations({
    required String studentId,
    String? subjectId,
    String? examId,
  }) async {
    final queryParams = <String, dynamic>{
      'studentId': studentId,
    };
    if (subjectId != null) queryParams['subjectId'] = subjectId;
    if (examId != null) queryParams['examId'] = examId;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/tutoring/recommendations').replace(
      queryParameters: queryParams
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取学习建议失败');
    }
  }
  
  /// 获取学习进度
  Future<Map<String, dynamic>> getLearningProgress({
    required String studentId,
    String? planId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final queryParams = <String, dynamic>{
      'studentId': studentId,
    };
    if (planId != null) queryParams['planId'] = planId;
    if (startDate != null) queryParams['startDate'] = startDate.toIso8601String();
    if (endDate != null) queryParams['endDate'] = endDate.toIso8601String();
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/tutoring/progress').replace(
      queryParameters: queryParams
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取学习进度失败');
    }
  }
  
  /// 更新学习进度
  Future<bool> updateLearningProgress({
    required String studentId,
    required String planId,
    required String taskId,
    required String status, // 'completed', 'in_progress', 'not_started'
    Map<String, dynamic>? result,
  }) async {
    final data = <String, dynamic>{
      'studentId': studentId,
      'planId': planId,
      'taskId': taskId,
      'status': status,
    };
    if (result != null) data['result'] = result;
    
    final response = await _apiClient.put<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/tutoring/progress',
      data: data,
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success) {
      return true;
    } else {
      throw Exception(response.message ?? '更新学习进度失败');
    }
  }
  
  /// 获取知识点掌握情况
  Future<Map<String, dynamic>> getKnowledgePointMastery({
    required String studentId,
    String? subjectId,
  }) async {
    final queryParams = <String, dynamic>{
      'studentId': studentId,
    };
    if (subjectId != null) queryParams['subjectId'] = subjectId;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/tutoring/knowledge/mastery').replace(
      queryParameters: queryParams
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取知识点掌握情况失败');
    }
  }
  
  /// 生成个性化学习路径
  Future<Map<String, dynamic>> generateLearningPath({
    required String studentId,
    required String subjectId,
    String? targetLevel,
    int? timeLimit, // 学习时间限制（天）
  }) async {
    final data = <String, dynamic>{
      'studentId': studentId,
      'subjectId': subjectId,
    };
    if (targetLevel != null) data['targetLevel'] = targetLevel;
    if (timeLimit != null) data['timeLimit'] = timeLimit;
    
    final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/tutoring/learning-path/generate',
      data: data,
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '生成学习路径失败');
    }
  }
}
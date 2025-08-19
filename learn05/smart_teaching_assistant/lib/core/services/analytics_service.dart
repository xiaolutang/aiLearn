import '../utils/api_client.dart';
import '../utils/constants.dart';

class AnalyticsService {
  final ApiClient _apiClient;
  
  AnalyticsService(this._apiClient);
  
  /// 获取班级成绩统计
  Future<Map<String, dynamic>> getClassStatistics({
    required String classId,
    String? examId,
    String? subjectId,
  }) async {
    final queryParams = <String, dynamic>{
      'classId': classId,
    };
    if (examId != null) queryParams['examId'] = examId;
    if (subjectId != null) queryParams['subjectId'] = subjectId;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/class/statistics').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取班级统计失败');
    }
  }
  
  /// 获取学生个人分析
  Future<Map<String, dynamic>> getStudentAnalysis({
    required String studentId,
    String? examId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final queryParams = <String, dynamic>{
      'studentId': studentId,
    };
    if (examId != null) queryParams['examId'] = examId;
    if (startDate != null) queryParams['startDate'] = startDate.toIso8601String();
    if (endDate != null) queryParams['endDate'] = endDate.toIso8601String();
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/student/analysis').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取学生分析失败');
    }
  }
  
  /// 获取年级排名分析
  Future<Map<String, dynamic>> getGradeRanking({
    required String gradeLevel,
    required String examId,
    String? subjectId,
  }) async {
    final queryParams = <String, dynamic>{
      'gradeLevel': gradeLevel,
      'examId': examId,
    };
    if (subjectId != null) queryParams['subjectId'] = subjectId;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/grade/ranking').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取年级排名失败');
    }
  }
  
  /// 获取分析概览
  Future<Map<String, dynamic>> getAnalyticsOverview({
    String timeRange = 'last_month',
  }) async {
    final queryParams = <String, dynamic>{
      'time_range': timeRange,
    };
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/overview').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取分析概览失败');
    }
  }
  
  /// 获取趋势分析
  Future<Map<String, dynamic>> getTrendAnalysis({
    String analysisType = 'score_trend',
    String? subject,
    String? className,
  }) async {
    final queryParams = <String, dynamic>{
      'analysis_type': analysisType,
    };
    if (subject != null) queryParams['subject'] = subject;
    if (className != null) queryParams['class_name'] = className;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/trends').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取趋势分析失败');
    }
  }
  
  /// 获取对比分析
  Future<Map<String, dynamic>> getComparisonAnalysis({
    required String comparisonType,
    required String baseline,
    required String target,
  }) async {
    final queryParams = <String, dynamic>{
      'comparison_type': comparisonType,
      'baseline': baseline,
      'target': target,
    };
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/comparison').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取对比分析失败');
    }
  }
  
  /// 获取预测分析
  Future<Map<String, dynamic>> getPredictiveAnalysis({
    String predictionType = 'performance_prediction',
    String? studentName,
    String? subject,
  }) async {
    final queryParams = <String, dynamic>{
      'prediction_type': predictionType,
    };
    if (studentName != null) queryParams['student_name'] = studentName;
    if (subject != null) queryParams['subject'] = subject;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/prediction').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取预测分析失败');
    }
  }
  
  /// 获取学科表现分析
  Future<Map<String, dynamic>> getSubjectPerformance({
    String? classId,
    String? examId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final queryParams = <String, dynamic>{};
    if (classId != null) queryParams['classId'] = classId;
    if (examId != null) queryParams['examId'] = examId;
    if (startDate != null) queryParams['startDate'] = startDate.toIso8601String();
    if (endDate != null) queryParams['endDate'] = endDate.toIso8601String();
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/subject/performance').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取学科表现失败');
    }
  }
  
  /// 获取成绩分布分析
  Future<Map<String, dynamic>> getScoreDistribution({
    String? classId,
    String? examId,
    String? subjectId,
  }) async {
    final queryParams = <String, dynamic>{};
    if (classId != null) queryParams['classId'] = classId;
    if (examId != null) queryParams['examId'] = examId;
    if (subjectId != null) queryParams['subjectId'] = subjectId;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/score/distribution').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取成绩分布失败');
    }
  }
  
  /// 获取学习进度分析
  Future<Map<String, dynamic>> getLearningProgress({
    required String studentId,
    String? subjectId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final queryParams = <String, dynamic>{
      'studentId': studentId,
    };
    if (subjectId != null) queryParams['subjectId'] = subjectId;
    if (startDate != null) queryParams['startDate'] = startDate.toIso8601String();
    if (endDate != null) queryParams['endDate'] = endDate.toIso8601String();
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/learning/progress').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
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
  
  /// 获取薄弱知识点分析
  Future<Map<String, dynamic>> getWeaknessAnalysis({
    required String studentId,
    String? subjectId,
    String? examId,
  }) async {
    final queryParams = <String, dynamic>{
      'studentId': studentId,
    };
    if (subjectId != null) queryParams['subjectId'] = subjectId;
    if (examId != null) queryParams['examId'] = examId;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/analytics/weakness/analysis').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取薄弱知识点分析失败');
    }
  }
}
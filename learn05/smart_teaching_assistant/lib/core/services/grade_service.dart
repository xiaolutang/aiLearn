import '../models/grade_model.dart';
import '../utils/api_client.dart';
import '../utils/constants.dart';

class GradeService {
  final ApiClient _apiClient;
  
  GradeService(this._apiClient);
  
  /// 获取成绩列表
  Future<GradeResponse> getGrades(GradeQueryParams params) async {
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/grades').replace(
      queryParameters: params.toJson().map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data != null) {
      return GradeResponse.fromJson(response.data!);
    } else {
      throw Exception(response.message ?? '获取成绩列表失败');
    }
  }
  
  /// 获取单个成绩详情
  Future<Grade> getGradeById(String gradeId) async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/grades/$gradeId',
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return Grade.fromJson(response.data!['data']);
    } else {
      throw Exception(response.message ?? '获取成绩详情失败');
    }
  }
  
  /// 批量录入成绩
  Future<bool> inputGrades(GradeInputRequest request) async {
    final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/grades/batch',
      data: request.toJson(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success) {
      return true;
    } else {
      throw Exception(response.message ?? '成绩录入失败');
    }
  }
  
  /// 更新单个成绩
  Future<bool> updateGrade(String gradeId, {
    double? score,
    String? remark,
  }) async {
    final data = <String, dynamic>{};
    if (score != null) data['score'] = score;
    if (remark != null) data['remark'] = remark;
    
    final response = await _apiClient.put<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/grades/$gradeId',
      data: data,
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success) {
      return true;
    } else {
      throw Exception(response.message ?? '更新成绩失败');
    }
  }
  
  /// 删除成绩
  Future<bool> deleteGrade(String gradeId) async {
    final response = await _apiClient.delete<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/grades/$gradeId',
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success) {
      return true;
    } else {
      throw Exception(response.message ?? '删除成绩失败');
    }
  }
  
  /// 创建考试
  Future<Exam> createExam({
    required String name,
    required String description,
    required String classId,
    required DateTime examDate,
    required List<String> subjectIds,
  }) async {
    final data = {
      'name': name,
      'description': description,
      'classId': classId,
      'examDate': examDate.toIso8601String(),
      'subjectIds': subjectIds,
    };
    
    final response = await _apiClient.post<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/exams',
      data: data,
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return Exam.fromJson(response.data!['data']);
    } else {
      throw Exception(response.message ?? '创建考试失败');
    }
  }

  /// 获取考试列表
  Future<List<Exam>> getExams({
    String? classId,
    String? status,
  }) async {
    final queryParams = <String, dynamic>{};
    if (classId != null) queryParams['classId'] = classId;
    if (status != null) queryParams['status'] = status;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/exams').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      final List<dynamic> examsList = response.data!['data'];
      return examsList.map((json) => Exam.fromJson(json)).toList();
    } else {
      throw Exception(response.message ?? '获取考试列表失败');
    }
  }
  
  /// 获取科目列表
  Future<List<Subject>> getSubjects() async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      '${ApiConstants.baseUrl}/api/v1/subjects',
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      final List<dynamic> subjectsList = response.data!['data'];
      return subjectsList.map((json) => Subject.fromJson(json)).toList();
    } else {
      throw Exception(response.message ?? '获取科目列表失败');
    }
  }
  
  /// 获取成绩统计
  Future<List<GradeStatistics>> getGradeStatistics({
    required String examId,
    String? classId,
  }) async {
    final queryParams = <String, dynamic>{
      'examId': examId,
    };
    if (classId != null) queryParams['classId'] = classId;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/grades/statistics').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      final List<dynamic> statsList = response.data!['data'];
      return statsList.map((json) => GradeStatistics.fromJson(json)).toList();
    } else {
      throw Exception(response.message ?? '获取成绩统计失败');
    }
  }
  
  /// 获取学生成绩分析
  Future<StudentGradeAnalysis> getStudentGradeAnalysis({
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
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/grades/analysis/student').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return StudentGradeAnalysis.fromJson(response.data!['data']);
    } else {
      throw Exception(response.message ?? '获取学生成绩分析失败');
    }
  }
  
  /// 获取班级成绩分析
  Future<Map<String, dynamic>> getClassGradeAnalysis({
    required String classId,
    required String examId,
  }) async {
    final queryParams = {
      'classId': classId,
      'examId': examId,
    };
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/grades/analysis/class').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取班级成绩分析失败');
    }
  }
  
  /// 导出成绩
  Future<String> exportGrades({
    required String examId,
    String? classId,
    String? format, // 'excel', 'pdf'
  }) async {
    final queryParams = <String, dynamic>{
      'examId': examId,
      'format': format ?? 'excel',
    };
    if (classId != null) queryParams['classId'] = classId;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/grades/export').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data']?['downloadUrl'] != null) {
      return response.data!['data']['downloadUrl'];
    } else {
      throw Exception(response.message ?? '导出成绩失败');
    }
  }
  
  /// 导入成绩
  Future<bool> importGrades({
    required String filePath,
    required String examId,
    required String subjectId,
  }) async {
    final response = await _apiClient.uploadFile(
      '${ApiConstants.baseUrl}/api/v1/grades/import',
      filePath,
      'file',
      fields: {
        'examId': examId,
        'subjectId': subjectId,
      },
    );
    
    final responseString = await response.stream.bytesToString();
    // 这里需要解析上传响应，假设返回JSON格式
    try {
      final responseData = Map<String, dynamic>.from(
        Uri.splitQueryString(responseString)
      );
      return responseData['success'] == 'true';
    } catch (e) {
      throw Exception('导入成绩失败: $e');
    }
  }
  
  /// 获取成绩趋势数据
  Future<Map<String, dynamic>> getGradeTrends({
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
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/grades/trends').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      return response.data!['data'];
    } else {
      throw Exception(response.message ?? '获取成绩趋势失败');
    }
  }
  
  /// 生成学习建议
  Future<List<String>> generateStudyRecommendations({
    required String studentId,
    String? examId,
  }) async {
    final queryParams = <String, dynamic>{
      'studentId': studentId,
    };
    if (examId != null) queryParams['examId'] = examId;
    
    final uri = Uri.parse('${ApiConstants.baseUrl}/api/v1/grades/recommendations').replace(
      queryParameters: queryParams.map((k, v) => MapEntry(k, v.toString()))
    );
    
    final response = await _apiClient.get<Map<String, dynamic>>(
      uri.toString(),
      fromJsonT: (json) => json as Map<String, dynamic>,
    );
    
    if (response.success && response.data?['data'] != null) {
      final List<dynamic> recommendations = response.data!['data'];
      return recommendations.cast<String>();
    } else {
      throw Exception(response.message ?? '生成学习建议失败');
    }
  }
}
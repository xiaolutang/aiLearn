import 'dart:io';
import 'package:http/http.dart' as http;
import '../utils/api_client.dart';
import '../utils/constants.dart';
import '../utils/app_logger.dart';
import '../utils/error_handler.dart';

/// 文件管理服务
class FileService {
  final ApiClient _apiClient = ApiClient();

  /// 上传文件
  Future<ErrorResult<Map<String, dynamic>>> uploadFile({
    required String filePath,
    required String fileType, // 'grade_import', 'student_photo', 'document', 'report'
    String? description,
    Map<String, String>? metadata,
    Function(int, int)? onProgress,
  }) async {
    try {
      final file = File(filePath);
      if (!await file.exists()) {
        return ErrorResult.failure(
          const FileException(message: 'File does not exist'),
        );
      }

      final fileName = file.path.split('/').last;
      
      AppLogger.userAction('Upload file', {
        'file_name': fileName,
        'file_type': fileType,
        'file_size': await file.length(),
      });

      final response = await _apiClient.uploadFileWithResponse<Map<String, dynamic>>(
        '${ApiConstants.baseUrl}/api/v1/files/upload',
        filePath,
        'file',
        fields: {
          'type': fileType,
          if (description != null) 'description': description,
          if (metadata != null) ...metadata,
        },
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        AppLogger.info('Successfully uploaded file: $fileName');
        return ErrorResult.success(response.data!);
      } else {
        const error = BusinessException(
          message: 'Failed to upload file',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to upload file', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }

  /// 下载文件
  Future<ErrorResult<String>> downloadFile({
    required String fileId,
    required String savePath,
    Function(int, int)? onProgress,
  }) async {
    try {
      AppLogger.userAction('Download file', {
        'file_id': fileId,
        'save_path': savePath,
      });

      final response = await _apiClient.get<Map<String, dynamic>>(
        '${ApiConstants.baseUrl}/api/v1/files/$fileId/download',
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        final downloadUrl = response.data!['download_url'] as String;
        
        // 下载文件内容
        final fileResponse = await http.get(Uri.parse(downloadUrl));
        if (fileResponse.statusCode == 200) {
          final file = File(savePath);
          await file.writeAsBytes(fileResponse.bodyBytes);
          
          AppLogger.info('Successfully downloaded file to: $savePath');
          return ErrorResult.success(savePath);
        } else {
          const error = BusinessException(
            message: 'Failed to download file content',
          );
          return ErrorResult.failure(error);
        }
      } else {
        const error = BusinessException(
          message: 'Failed to get download URL',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to download file', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }

  /// 获取文件信息
  Future<ErrorResult<Map<String, dynamic>>> getFileInfo(String fileId) async {
    try {
      AppLogger.userAction('Get file info', {'file_id': fileId});

      final response = await _apiClient.get<Map<String, dynamic>>(
        '${ApiConstants.baseUrl}/api/v1/files/$fileId',
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        AppLogger.info('Successfully retrieved file info');
        return ErrorResult.success(response.data!);
      } else {
        const error = BusinessException(
          message: 'Failed to get file info',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to get file info', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }

  /// 删除文件
  Future<ErrorResult<bool>> deleteFile(String fileId) async {
    try {
      AppLogger.userAction('Delete file', {'file_id': fileId});

      final response = await _apiClient.delete<Map<String, dynamic>>(
        '${ApiConstants.baseUrl}/api/v1/files/$fileId',
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success) {
        AppLogger.info('Successfully deleted file');
        return ErrorResult.success(true);
      } else {
        const error = BusinessException(
          message: 'Failed to delete file',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to delete file', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }

  /// 获取文件列表
  Future<ErrorResult<List<Map<String, dynamic>>>> getFileList({
    String? fileType,
    int page = 1,
    int limit = 20,
  }) async {
    try {
      AppLogger.userAction('Get file list', {
        'file_type': fileType,
        'page': page,
        'limit': limit,
      });

      final queryParams = <String, String>{
        'page': page.toString(),
        'limit': limit.toString(),
        if (fileType != null) 'type': fileType,
      };

      final url = '${ApiConstants.baseUrl}/api/v1/files?${Uri(queryParameters: queryParams).query}';
      final response = await _apiClient.get<Map<String, dynamic>>(
        url,
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        final files = (response.data!['data'] as List)
            .map((item) => item as Map<String, dynamic>)
            .toList();
        AppLogger.info('Successfully retrieved file list');
        return ErrorResult.success(files);
      } else {
        const error = BusinessException(
          message: 'Failed to get file list',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to get file list', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }

  /// 导入成绩文件
  Future<ErrorResult<Map<String, dynamic>>> importGrades({
    required String filePath,
    required String classId,
    required String examId,
    String? description,
  }) async {
    try {
      AppLogger.userAction('Import grades', {
        'class_id': classId,
        'exam_id': examId,
        'file_path': filePath,
      });

      final response = await _apiClient.uploadFileWithResponse<Map<String, dynamic>>(
        '${ApiConstants.baseUrl}/api/v1/grades/import',
        filePath,
        'file',
        fields: {
          'class_id': classId,
          'exam_id': examId,
          if (description != null) 'description': description,
        },
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        AppLogger.info('Successfully imported grades');
        return ErrorResult.success(response.data!);
      } else {
        const error = BusinessException(
          message: 'Failed to import grades',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to import grades', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }

  /// 导出成绩文件
  Future<ErrorResult<String>> exportGrades({
    required String classId,
    required String examId,
    required String savePath,
    String format = 'xlsx', // 'xlsx', 'csv', 'pdf'
  }) async {
    try {
      AppLogger.userAction('Export grades', {
        'class_id': classId,
        'exam_id': examId,
        'format': format,
      });

      final queryParams = {
        'class_id': classId,
        'exam_id': examId,
        'format': format,
      };

      final url = '${ApiConstants.baseUrl}/api/v1/grades/export?${Uri(queryParameters: queryParams).query}';
      final response = await _apiClient.get<Map<String, dynamic>>(
        url,
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        final downloadUrl = response.data!['download_url'] as String;
        
        // 下载文件内容
        final fileResponse = await http.get(Uri.parse(downloadUrl));
        if (fileResponse.statusCode == 200) {
          final file = File(savePath);
          await file.writeAsBytes(fileResponse.bodyBytes);
          
          AppLogger.info('Successfully exported grades to: $savePath');
          return ErrorResult.success(savePath);
        } else {
          const error = BusinessException(
            message: 'Failed to download exported file',
          );
          return ErrorResult.failure(error);
        }
      } else {
        const error = BusinessException(
          message: 'Failed to export grades',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to export grades', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }

  /// 导入学生数据
  Future<ErrorResult<Map<String, dynamic>>> importStudents({
    required String filePath,
    required String classId,
    String? description,
  }) async {
    try {
      AppLogger.userAction('Import students', {
        'class_id': classId,
        'file_path': filePath,
      });

      final response = await _apiClient.uploadFileWithResponse<Map<String, dynamic>>(
        '${ApiConstants.baseUrl}/api/v1/students/import',
        filePath,
        'file',
        fields: {
          'class_id': classId,
          if (description != null) 'description': description,
        },
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        AppLogger.info('Successfully imported students');
        return ErrorResult.success(response.data!);
      } else {
        const error = BusinessException(
          message: 'Failed to import students',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to import students', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }

  /// 导出学生数据
  Future<ErrorResult<String>> exportStudents({
    required String classId,
    required String savePath,
    String format = 'xlsx', // 'xlsx', 'csv'
  }) async {
    try {
      AppLogger.userAction('Export students', {
        'class_id': classId,
        'format': format,
      });

      final queryParams = {
        'class_id': classId,
        'format': format,
      };

      final url = '${ApiConstants.baseUrl}/api/v1/students/export?${Uri(queryParameters: queryParams).query}';
      final response = await _apiClient.get<Map<String, dynamic>>(
        url,
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        final downloadUrl = response.data!['download_url'] as String;
        
        // 下载文件内容
        final fileResponse = await http.get(Uri.parse(downloadUrl));
        if (fileResponse.statusCode == 200) {
          final file = File(savePath);
          await file.writeAsBytes(fileResponse.bodyBytes);
          
          AppLogger.info('Successfully exported students to: $savePath');
          return ErrorResult.success(savePath);
        } else {
          const error = BusinessException(
            message: 'Failed to download exported file',
          );
          return ErrorResult.failure(error);
        }
      } else {
        const error = BusinessException(
          message: 'Failed to export students',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to export students', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }

  /// 生成分析报告
  Future<ErrorResult<String>> generateAnalysisReport({
    required String reportType, // 'class_analysis', 'student_analysis', 'grade_analysis'
    required Map<String, dynamic> parameters,
    required String savePath,
    String format = 'pdf', // 'pdf', 'docx'
  }) async {
    try {
      AppLogger.userAction('Generate analysis report', {
        'report_type': reportType,
        'format': format,
        'parameters': parameters,
      });

      final response = await _apiClient.post<Map<String, dynamic>>(
        '${ApiConstants.baseUrl}/api/v1/reports/generate',
        data: {
          'type': reportType,
          'format': format,
          'parameters': parameters,
        },
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        final downloadUrl = response.data!['download_url'] as String;
        
        // 下载文件内容
        final fileResponse = await http.get(Uri.parse(downloadUrl));
        if (fileResponse.statusCode == 200) {
          final file = File(savePath);
          await file.writeAsBytes(fileResponse.bodyBytes);
          
          AppLogger.info('Successfully generated analysis report: $savePath');
          return ErrorResult.success(savePath);
        } else {
          const error = BusinessException(
            message: 'Failed to download generated report',
          );
          return ErrorResult.failure(error);
        }
      } else {
        const error = BusinessException(
          message: 'Failed to generate analysis report',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to generate analysis report', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }

  /// 获取文件模板
  Future<ErrorResult<String>> getFileTemplate({
    required String templateType, // 'grade_import', 'student_import'
    required String savePath,
  }) async {
    try {
      AppLogger.userAction('Get file template', {
        'template_type': templateType,
      });

      final response = await _apiClient.get<Map<String, dynamic>>(
        '${ApiConstants.baseUrl}/api/v1/files/templates/$templateType',
        fromJsonT: (json) => json as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        final downloadUrl = response.data!['download_url'] as String;
        
        // 下载文件内容
        final fileResponse = await http.get(Uri.parse(downloadUrl));
        if (fileResponse.statusCode == 200) {
          final file = File(savePath);
          await file.writeAsBytes(fileResponse.bodyBytes);
          
          AppLogger.info('Successfully downloaded template: $savePath');
          return ErrorResult.success(savePath);
        } else {
          const error = BusinessException(
            message: 'Failed to download template file',
          );
          return ErrorResult.failure(error);
        }
      } else {
        const error = BusinessException(
          message: 'Failed to get file template',
        );
        return ErrorResult.failure(error);
      }
    } catch (e, stackTrace) {
      final error = ErrorHandler.handleError(e, stackTrace);
      AppLogger.error('Failed to get file template', e, stackTrace);
      return ErrorResult.failure(error);
    }
  }
}
-- ==========================================
-- 智能教学助手2.0 数据库设计文档
-- ==========================================
-- 
-- 本文件定义了智能教学助手2.0的完整数据库结构
-- 包含用户管理、教学内容、AI分析结果等核心数据表
-- 
-- @version 2.0.0
-- @date 2024-12-15
-- @database MySQL 8.0+
-- ==========================================

-- 设置字符集和排序规则
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ==========================================
-- 1. 用户与权限管理
-- ==========================================

-- 学校信息表
CREATE TABLE `schools` (
  `school_id` varchar(32) NOT NULL COMMENT '学校ID',
  `school_name` varchar(100) NOT NULL COMMENT '学校名称',
  `school_code` varchar(20) NOT NULL COMMENT '学校代码',
  `school_type` enum('小学','初中','高中','大学','其他') NOT NULL DEFAULT '高中' COMMENT '学校类型',
  `region` varchar(100) NOT NULL COMMENT '所在地区',
  `address` text COMMENT '详细地址',
  `contact_phone` varchar(20) COMMENT '联系电话',
  `contact_email` varchar(100) COMMENT '联系邮箱',
  `principal_name` varchar(50) COMMENT '校长姓名',
  `established_date` date COMMENT '建校日期',
  `student_count` int DEFAULT 0 COMMENT '学生总数',
  `teacher_count` int DEFAULT 0 COMMENT '教师总数',
  `status` enum('active','inactive','suspended') NOT NULL DEFAULT 'active' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`school_id`),
  UNIQUE KEY `uk_school_code` (`school_code`),
  KEY `idx_school_region` (`region`),
  KEY `idx_school_type` (`school_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学校信息表';

-- 用户表
CREATE TABLE `users` (
  `user_id` varchar(32) NOT NULL COMMENT '用户ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password_hash` varchar(255) NOT NULL COMMENT '密码哈希',
  `real_name` varchar(50) NOT NULL COMMENT '真实姓名',
  `email` varchar(100) NOT NULL COMMENT '邮箱',
  `phone` varchar(20) NOT NULL COMMENT '手机号',
  `avatar` varchar(255) COMMENT '头像URL',
  `role` enum('teacher','student','admin','super_admin') NOT NULL DEFAULT 'teacher' COMMENT '用户角色',
  `status` enum('active','inactive','suspended','pending') NOT NULL DEFAULT 'pending' COMMENT '用户状态',
  `school_id` varchar(32) NOT NULL COMMENT '所属学校ID',
  `employee_id` varchar(50) COMMENT '工号/学号',
  `gender` enum('male','female','other') COMMENT '性别',
  `birth_date` date COMMENT '出生日期',
  `id_card` varchar(18) COMMENT '身份证号',
  `last_login` timestamp NULL COMMENT '最后登录时间',
  `login_count` int DEFAULT 0 COMMENT '登录次数',
  `email_verified` tinyint(1) DEFAULT 0 COMMENT '邮箱是否验证',
  `phone_verified` tinyint(1) DEFAULT 0 COMMENT '手机是否验证',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`),
  UNIQUE KEY `uk_phone` (`phone`),
  KEY `idx_school_id` (`school_id`),
  KEY `idx_role` (`role`),
  KEY `idx_status` (`status`),
  KEY `idx_employee_id` (`employee_id`),
  CONSTRAINT `fk_users_school` FOREIGN KEY (`school_id`) REFERENCES `schools` (`school_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 教师档案表
CREATE TABLE `teacher_profiles` (
  `user_id` varchar(32) NOT NULL COMMENT '用户ID',
  `subject` varchar(50) NOT NULL COMMENT '主教学科',
  `grade_levels` json NOT NULL COMMENT '教学年级（JSON数组）',
  `teaching_years` int DEFAULT 0 COMMENT '教龄',
  `education_background` varchar(100) COMMENT '学历背景',
  `certification` varchar(100) COMMENT '职业资格',
  `specialties` json COMMENT '专业特长（JSON数组）',
  `research_interests` text COMMENT '研究兴趣',
  `awards` json COMMENT '获奖情况（JSON数组）',
  `publications` json COMMENT '发表论文（JSON数组）',
  `training_records` json COMMENT '培训记录（JSON数组）',
  `performance_rating` decimal(3,2) DEFAULT 0.00 COMMENT '绩效评分',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_id`),
  KEY `idx_subject` (`subject`),
  KEY `idx_teaching_years` (`teaching_years`),
  CONSTRAINT `fk_teacher_profiles_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教师档案表';

-- 用户偏好设置表
CREATE TABLE `user_preferences` (
  `user_id` varchar(32) NOT NULL COMMENT '用户ID',
  `theme` enum('light','dark','auto') DEFAULT 'light' COMMENT '主题设置',
  `language` varchar(10) DEFAULT 'zh-CN' COMMENT '语言设置',
  `timezone` varchar(50) DEFAULT 'Asia/Shanghai' COMMENT '时区设置',
  `notification_email` tinyint(1) DEFAULT 1 COMMENT '邮件通知',
  `notification_sms` tinyint(1) DEFAULT 0 COMMENT '短信通知',
  `notification_push` tinyint(1) DEFAULT 1 COMMENT '推送通知',
  `ai_assistance_level` enum('basic','standard','advanced') DEFAULT 'standard' COMMENT 'AI辅助级别',
  `auto_save_interval` int DEFAULT 300 COMMENT '自动保存间隔（秒）',
  `dashboard_layout` json COMMENT '工作台布局配置',
  `quick_actions` json COMMENT '快速操作配置',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_id`),
  CONSTRAINT `fk_user_preferences_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户偏好设置表';

-- ==========================================
-- 2. 班级与学生管理
-- ==========================================

-- 班级表
CREATE TABLE `classes` (
  `class_id` varchar(32) NOT NULL COMMENT '班级ID',
  `class_name` varchar(50) NOT NULL COMMENT '班级名称',
  `grade` varchar(20) NOT NULL COMMENT '年级',
  `school_id` varchar(32) NOT NULL COMMENT '学校ID',
  `head_teacher_id` varchar(32) COMMENT '班主任ID',
  `student_count` int DEFAULT 0 COMMENT '学生人数',
  `classroom` varchar(50) COMMENT '教室',
  `academic_year` varchar(20) NOT NULL COMMENT '学年',
  `semester` enum('spring','autumn') NOT NULL COMMENT '学期',
  `status` enum('active','inactive','graduated') NOT NULL DEFAULT 'active' COMMENT '状态',
  `description` text COMMENT '班级描述',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`class_id`),
  KEY `idx_school_id` (`school_id`),
  KEY `idx_head_teacher_id` (`head_teacher_id`),
  KEY `idx_grade` (`grade`),
  KEY `idx_academic_year` (`academic_year`),
  CONSTRAINT `fk_classes_school` FOREIGN KEY (`school_id`) REFERENCES `schools` (`school_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_classes_head_teacher` FOREIGN KEY (`head_teacher_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班级表';

-- 学生表
CREATE TABLE `students` (
  `student_id` varchar(32) NOT NULL COMMENT '学生ID',
  `user_id` varchar(32) COMMENT '关联用户ID（如果学生有账号）',
  `student_name` varchar(50) NOT NULL COMMENT '学生姓名',
  `student_number` varchar(50) NOT NULL COMMENT '学号',
  `class_id` varchar(32) NOT NULL COMMENT '班级ID',
  `gender` enum('male','female','other') COMMENT '性别',
  `birth_date` date COMMENT '出生日期',
  `id_card` varchar(18) COMMENT '身份证号',
  `phone` varchar(20) COMMENT '联系电话',
  `email` varchar(100) COMMENT '邮箱',
  `address` text COMMENT '家庭地址',
  `parent_name` varchar(50) COMMENT '家长姓名',
  `parent_phone` varchar(20) COMMENT '家长电话',
  `parent_email` varchar(100) COMMENT '家长邮箱',
  `enrollment_date` date NOT NULL COMMENT '入学日期',
  `graduation_date` date COMMENT '毕业日期',
  `status` enum('active','inactive','transferred','graduated','dropped') NOT NULL DEFAULT 'active' COMMENT '状态',
  `notes` text COMMENT '备注',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `uk_student_number` (`student_number`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_class_id` (`class_id`),
  KEY `idx_student_name` (`student_name`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_students_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_students_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`class_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生表';

-- ==========================================
-- 3. 课程与教学内容
-- ==========================================

-- 课程表
CREATE TABLE `courses` (
  `course_id` varchar(32) NOT NULL COMMENT '课程ID',
  `course_name` varchar(100) NOT NULL COMMENT '课程名称',
  `course_code` varchar(20) NOT NULL COMMENT '课程代码',
  `subject` varchar(50) NOT NULL COMMENT '学科',
  `grade` varchar(20) NOT NULL COMMENT '年级',
  `semester` enum('spring','autumn','summer') NOT NULL COMMENT '学期',
  `academic_year` varchar(20) NOT NULL COMMENT '学年',
  `teacher_id` varchar(32) NOT NULL COMMENT '任课教师ID',
  `class_ids` json NOT NULL COMMENT '授课班级ID列表',
  `total_hours` int NOT NULL COMMENT '总课时',
  `weekly_hours` int NOT NULL COMMENT '周课时',
  `textbook_info` json COMMENT '教材信息',
  `course_objectives` text COMMENT '课程目标',
  `course_outline` text COMMENT '课程大纲',
  `assessment_methods` json COMMENT '考核方式',
  `status` enum('planning','active','completed','cancelled') NOT NULL DEFAULT 'planning' COMMENT '状态',
  `start_date` date NOT NULL COMMENT '开始日期',
  `end_date` date NOT NULL COMMENT '结束日期',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`course_id`),
  UNIQUE KEY `uk_course_code` (`course_code`),
  KEY `idx_teacher_id` (`teacher_id`),
  KEY `idx_subject` (`subject`),
  KEY `idx_grade` (`grade`),
  KEY `idx_academic_year` (`academic_year`),
  CONSTRAINT `fk_courses_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';

-- 教学内容表
CREATE TABLE `teaching_contents` (
  `content_id` varchar(32) NOT NULL COMMENT '内容ID',
  `course_id` varchar(32) NOT NULL COMMENT '课程ID',
  `chapter` varchar(100) NOT NULL COMMENT '章节',
  `section` varchar(100) COMMENT '小节',
  `title` varchar(200) NOT NULL COMMENT '标题',
  `content_type` enum('theory','experiment','practice','review','exam') NOT NULL DEFAULT 'theory' COMMENT '内容类型',
  `knowledge_points` json COMMENT '知识点列表',
  `difficulty_level` int DEFAULT 1 COMMENT '难度等级（1-5）',
  `estimated_hours` decimal(4,2) DEFAULT 1.00 COMMENT '预计课时',
  `learning_objectives` text COMMENT '学习目标',
  `key_points` text COMMENT '重点内容',
  `difficult_points` text COMMENT '难点内容',
  `teaching_methods` json COMMENT '教学方法',
  `resources` json COMMENT '教学资源',
  `prerequisites` json COMMENT '前置知识',
  `sequence_order` int NOT NULL COMMENT '顺序',
  `status` enum('draft','published','archived') NOT NULL DEFAULT 'draft' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`content_id`),
  KEY `idx_course_id` (`course_id`),
  KEY `idx_sequence_order` (`sequence_order`),
  KEY `idx_difficulty_level` (`difficulty_level`),
  CONSTRAINT `fk_teaching_contents_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教学内容表';

-- ==========================================
-- 4. 备课与教案管理
-- ==========================================

-- 备课记录表
CREATE TABLE `lesson_preparations` (
  `preparation_id` varchar(32) NOT NULL COMMENT '备课ID',
  `teacher_id` varchar(32) NOT NULL COMMENT '教师ID',
  `content_id` varchar(32) NOT NULL COMMENT '教学内容ID',
  `lesson_title` varchar(200) NOT NULL COMMENT '课题',
  `lesson_type` enum('new','review','practice','experiment','assessment') NOT NULL DEFAULT 'new' COMMENT '课型',
  `target_classes` json NOT NULL COMMENT '目标班级',
  `scheduled_date` date COMMENT '计划上课日期',
  `estimated_duration` int DEFAULT 45 COMMENT '预计时长（分钟）',
  `preparation_status` enum('draft','in_progress','completed','reviewed') NOT NULL DEFAULT 'draft' COMMENT '备课状态',
  `lesson_objectives` text COMMENT '教学目标',
  `lesson_structure` json COMMENT '课程结构',
  `teaching_activities` json COMMENT '教学活动',
  `resources_needed` json COMMENT '所需资源',
  `assessment_plan` json COMMENT '评估计划',
  `differentiation_strategies` json COMMENT '差异化策略',
  `potential_challenges` json COMMENT '潜在挑战',
  `reflection_notes` text COMMENT '反思笔记',
  `ai_suggestions` json COMMENT 'AI建议',
  `preparation_time` int DEFAULT 0 COMMENT '备课用时（分钟）',
  `quality_score` decimal(3,2) DEFAULT 0.00 COMMENT '质量评分',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`preparation_id`),
  KEY `idx_teacher_id` (`teacher_id`),
  KEY `idx_content_id` (`content_id`),
  KEY `idx_scheduled_date` (`scheduled_date`),
  KEY `idx_preparation_status` (`preparation_status`),
  CONSTRAINT `fk_lesson_preparations_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_lesson_preparations_content` FOREIGN KEY (`content_id`) REFERENCES `teaching_contents` (`content_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='备课记录表';

-- 教材分析记录表
CREATE TABLE `textbook_analyses` (
  `analysis_id` varchar(32) NOT NULL COMMENT '分析ID',
  `teacher_id` varchar(32) NOT NULL COMMENT '教师ID',
  `textbook_info` json NOT NULL COMMENT '教材信息',
  `analysis_scope` json NOT NULL COMMENT '分析范围',
  `knowledge_points` json COMMENT '知识点分析',
  `difficulty_analysis` json COMMENT '难度分析',
  `teaching_objectives` json COMMENT '教学目标',
  `teaching_suggestions` json COMMENT '教学建议',
  `experiment_recommendations` json COMMENT '实验推荐',
  `assessment_suggestions` json COMMENT '评估建议',
  `ai_confidence` decimal(3,2) DEFAULT 0.00 COMMENT 'AI置信度',
  `analysis_time` int DEFAULT 0 COMMENT '分析用时（秒）',
  `feedback_rating` int COMMENT '用户反馈评分（1-5）',
  `feedback_comments` text COMMENT '用户反馈意见',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`analysis_id`),
  KEY `idx_teacher_id` (`teacher_id`),
  KEY `idx_ai_confidence` (`ai_confidence`),
  CONSTRAINT `fk_textbook_analyses_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教材分析记录表';

-- ==========================================
-- 5. 课堂教学与实时分析
-- ==========================================

-- 课堂记录表
CREATE TABLE `classroom_sessions` (
  `session_id` varchar(32) NOT NULL COMMENT '课堂会话ID',
  `preparation_id` varchar(32) NOT NULL COMMENT '备课记录ID',
  `teacher_id` varchar(32) NOT NULL COMMENT '教师ID',
  `class_id` varchar(32) NOT NULL COMMENT '班级ID',
  `lesson_title` varchar(200) NOT NULL COMMENT '课题',
  `start_time` timestamp NOT NULL COMMENT '开始时间',
  `end_time` timestamp NULL COMMENT '结束时间',
  `actual_duration` int COMMENT '实际时长（分钟）',
  `attendance_count` int COMMENT '出勤人数',
  `session_status` enum('scheduled','ongoing','completed','cancelled') NOT NULL DEFAULT 'scheduled' COMMENT '课堂状态',
  `teaching_mode` enum('traditional','interactive','hybrid','online') NOT NULL DEFAULT 'traditional' COMMENT '教学模式',
  `classroom_location` varchar(100) COMMENT '教室位置',
  `recording_enabled` tinyint(1) DEFAULT 0 COMMENT '是否启用录制',
  `ai_analysis_enabled` tinyint(1) DEFAULT 1 COMMENT '是否启用AI分析',
  `session_notes` text COMMENT '课堂笔记',
  `technical_issues` text COMMENT '技术问题记录',
  `overall_rating` decimal(3,2) COMMENT '整体评分',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`session_id`),
  KEY `idx_preparation_id` (`preparation_id`),
  KEY `idx_teacher_id` (`teacher_id`),
  KEY `idx_class_id` (`class_id`),
  KEY `idx_start_time` (`start_time`),
  KEY `idx_session_status` (`session_status`),
  CONSTRAINT `fk_classroom_sessions_preparation` FOREIGN KEY (`preparation_id`) REFERENCES `lesson_preparations` (`preparation_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_classroom_sessions_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_classroom_sessions_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`class_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课堂记录表';

-- 学情分析记录表
CREATE TABLE `learning_state_analyses` (
  `analysis_id` varchar(32) NOT NULL COMMENT '分析ID',
  `session_id` varchar(32) NOT NULL COMMENT '课堂会话ID',
  `question_data` json NOT NULL COMMENT '问题数据',
  `student_responses` json NOT NULL COMMENT '学生回答数据',
  `analysis_context` json COMMENT '分析上下文',
  `question_analysis` json COMMENT '问题分析结果',
  `individual_analysis` json COMMENT '个体分析结果',
  `class_insights` json COMMENT '班级洞察',
  `recommendations` json COMMENT '教学建议',
  `confidence_score` decimal(3,2) DEFAULT 0.00 COMMENT '置信度评分',
  `analysis_time` int DEFAULT 0 COMMENT '分析用时（毫秒）',
  `feedback_applied` tinyint(1) DEFAULT 0 COMMENT '建议是否被采纳',
  `effectiveness_rating` int COMMENT '效果评分（1-5）',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`analysis_id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_confidence_score` (`confidence_score`),
  CONSTRAINT `fk_learning_state_analyses_session` FOREIGN KEY (`session_id`) REFERENCES `classroom_sessions` (`session_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学情分析记录表';

-- 实验设计记录表
CREATE TABLE `experiment_designs` (
  `experiment_id` varchar(32) NOT NULL COMMENT '实验ID',
  `teacher_id` varchar(32) NOT NULL COMMENT '教师ID',
  `content_id` varchar(32) COMMENT '关联教学内容ID',
  `experiment_title` varchar(200) NOT NULL COMMENT '实验标题',
  `experiment_type` enum('demonstration','group','individual') NOT NULL DEFAULT 'group' COMMENT '实验类型',
  `difficulty_level` int DEFAULT 1 COMMENT '难度等级（1-5）',
  `estimated_duration` int NOT NULL COMMENT '预计时长（分钟）',
  `group_size` int DEFAULT 4 COMMENT '小组人数',
  `group_count` int DEFAULT 1 COMMENT '小组数量',
  `requirements` json NOT NULL COMMENT '实验需求',
  `preferences` json COMMENT '实验偏好',
  `learning_objectives` json COMMENT '学习目标',
  `materials_list` json COMMENT '材料清单',
  `experimental_procedure` json COMMENT '实验程序',
  `safety_guidelines` json COMMENT '安全指南',
  `assessment_criteria` json COMMENT '评估标准',
  `troubleshooting` json COMMENT '故障排除',
  `extension_activities` json COMMENT '扩展活动',
  `ai_optimization_suggestions` json COMMENT 'AI优化建议',
  `confidence_score` decimal(3,2) DEFAULT 0.00 COMMENT '置信度评分',
  `usage_count` int DEFAULT 0 COMMENT '使用次数',
  `average_rating` decimal(3,2) DEFAULT 0.00 COMMENT '平均评分',
  `status` enum('draft','published','archived') NOT NULL DEFAULT 'draft' COMMENT '状态',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`experiment_id`),
  KEY `idx_teacher_id` (`teacher_id`),
  KEY `idx_content_id` (`content_id`),
  KEY `idx_experiment_type` (`experiment_type`),
  KEY `idx_difficulty_level` (`difficulty_level`),
  CONSTRAINT `fk_experiment_designs_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_experiment_designs_content` FOREIGN KEY (`content_id`) REFERENCES `teaching_contents` (`content_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='实验设计记录表';

-- ==========================================
-- 6. 成绩管理
-- ==========================================

-- 考试信息表
CREATE TABLE `exams` (
  `exam_id` varchar(32) NOT NULL COMMENT '考试ID',
  `exam_name` varchar(200) NOT NULL COMMENT '考试名称',
  `exam_type` enum('quiz','midterm','final','homework','project') NOT NULL DEFAULT 'quiz' COMMENT '考试类型',
  `course_id` varchar(32) NOT NULL COMMENT '课程ID',
  `teacher_id` varchar(32) NOT NULL COMMENT '出题教师ID',
  `subject` varchar(50) NOT NULL COMMENT '学科',
  `exam_date` date NOT NULL COMMENT '考试日期',
  `start_time` time COMMENT '开始时间',
  `duration` int COMMENT '考试时长（分钟）',
  `full_score` decimal(6,2) NOT NULL COMMENT '满分',
  `pass_score` decimal(6,2) COMMENT '及格分',
  `class_ids` json NOT NULL COMMENT '参考班级ID列表',
  `exam_scope` text COMMENT '考试范围',
  `question_structure` json COMMENT '题目结构',
  `scoring_rules` json COMMENT '评分规则',
  `exam_location` varchar(100) COMMENT '考试地点',
  `exam_status` enum('draft','published','ongoing','completed','cancelled') NOT NULL DEFAULT 'draft' COMMENT '考试状态',
  `instructions` text COMMENT '考试说明',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`exam_id`),
  KEY `idx_course_id` (`course_id`),
  KEY `idx_teacher_id` (`teacher_id`),
  KEY `idx_exam_date` (`exam_date`),
  KEY `idx_exam_type` (`exam_type`),
  CONSTRAINT `fk_exams_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_exams_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`user_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试信息表';

-- 成绩记录表
CREATE TABLE `grade_records` (
  `record_id` varchar(32) NOT NULL COMMENT '记录ID',
  `exam_id` varchar(32) NOT NULL COMMENT '考试ID',
  `student_id` varchar(32) NOT NULL COMMENT '学生ID',
  `total_score` decimal(6,2) NOT NULL COMMENT '总分',
  `section_scores` json COMMENT '分项得分',
  `knowledge_point_scores` json COMMENT '知识点得分',
  `rank_in_class` int COMMENT '班级排名',
  `rank_in_grade` int COMMENT '年级排名',
  `percentile` decimal(5,2) COMMENT '百分位数',
  `grade_level` enum('A+','A','A-','B+','B','B-','C+','C','C-','D','F') COMMENT '等级',
  `is_absent` tinyint(1) DEFAULT 0 COMMENT '是否缺考',
  `is_cheating` tinyint(1) DEFAULT 0 COMMENT '是否作弊',
  `submission_time` timestamp COMMENT '提交时间',
  `grading_time` timestamp COMMENT '批改时间',
  `grader_id` varchar(32) COMMENT '批改教师ID',
  `grading_method` enum('manual','auto','ai_assisted') DEFAULT 'manual' COMMENT '批改方式',
  `comments` text COMMENT '评语',
  `improvement_suggestions` text COMMENT '改进建议',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`record_id`),
  UNIQUE KEY `uk_exam_student` (`exam_id`, `student_id`),
  KEY `idx_student_id` (`student_id`),
  KEY `idx_total_score` (`total_score`),
  KEY `idx_grader_id` (`grader_id`),
  CONSTRAINT `fk_grade_records_exam` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`exam_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_grade_records_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_grade_records_grader` FOREIGN KEY (`grader_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成绩记录表';

-- 成绩分析结果表
CREATE TABLE `grade_analyses` (
  `analysis_id` varchar(32) NOT NULL COMMENT '分析ID',
  `exam_id` varchar(32) NOT NULL COMMENT '考试ID',
  `teacher_id` varchar(32) NOT NULL COMMENT '教师ID',
  `analysis_scope` json NOT NULL COMMENT '分析范围',
  `overall_statistics` json COMMENT '整体统计',
  `class_comparison` json COMMENT '班级对比',
  `knowledge_point_analysis` json COMMENT '知识点分析',
  `individual_insights` json COMMENT '个人洞察',
  `ai_insights` json COMMENT 'AI洞察',
  `recommended_actions` json COMMENT '推荐行动',
  `analysis_quality` decimal(3,2) DEFAULT 0.00 COMMENT '分析质量评分',
  `processing_time` int DEFAULT 0 COMMENT '处理时间（秒）',
  `viewed_count` int DEFAULT 0 COMMENT '查看次数',
  `shared_count` int DEFAULT 0 COMMENT '分享次数',
  `feedback_rating` int COMMENT '用户反馈评分（1-5）',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`analysis_id`),
  KEY `idx_exam_id` (`exam_id`),
  KEY `idx_teacher_id` (`teacher_id`),
  KEY `idx_analysis_quality` (`analysis_quality`),
  CONSTRAINT `fk_grade_analyses_exam` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`exam_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_grade_analyses_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成绩分析结果表';

-- ==========================================
-- 7. AI服务与分析
-- ==========================================

-- AI聊天会话表
CREATE TABLE `ai_chat_sessions` (
  `session_id` varchar(32) NOT NULL COMMENT '会话ID',
  `user_id` varchar(32) NOT NULL COMMENT '用户ID',
  `session_title` varchar(200) COMMENT '会话标题',
  `session_type` enum('general','teaching','grading','experiment','analysis') NOT NULL DEFAULT 'general' COMMENT '会话类型',
  `context_info` json COMMENT '上下文信息',
  `message_count` int DEFAULT 0 COMMENT '消息数量',
  `total_tokens` int DEFAULT 0 COMMENT '总token数',
  `session_status` enum('active','paused','completed','archived') NOT NULL DEFAULT 'active' COMMENT '会话状态',
  `last_activity` timestamp NULL COMMENT '最后活动时间',
  `satisfaction_rating` int COMMENT '满意度评分（1-5）',
  `feedback_comments` text COMMENT '反馈意见',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`session_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_session_type` (`session_type`),
  KEY `idx_last_activity` (`last_activity`),
  CONSTRAINT `fk_ai_chat_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI聊天会话表';

-- AI聊天消息表
CREATE TABLE `ai_chat_messages` (
  `message_id` varchar(32) NOT NULL COMMENT '消息ID',
  `session_id` varchar(32) NOT NULL COMMENT '会话ID',
  `message_type` enum('user','assistant','system') NOT NULL COMMENT '消息类型',
  `content_type` enum('text','image','voice','file') NOT NULL DEFAULT 'text' COMMENT '内容类型',
  `message_content` text NOT NULL COMMENT '消息内容',
  `attachments` json COMMENT '附件信息',
  `context_data` json COMMENT '上下文数据',
  `ai_model` varchar(50) COMMENT '使用的AI模型',
  `token_count` int DEFAULT 0 COMMENT 'token数量',
  `processing_time` int DEFAULT 0 COMMENT '处理时间（毫秒）',
  `confidence_score` decimal(3,2) COMMENT '置信度评分',
  `feedback_rating` int COMMENT '消息反馈评分（1-5）',
  `is_helpful` tinyint(1) COMMENT '是否有帮助',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`message_id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_message_type` (`message_type`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_ai_chat_messages_session` FOREIGN KEY (`session_id`) REFERENCES `ai_chat_sessions` (`session_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI聊天消息表';

-- 学生学习画像表
CREATE TABLE `student_learning_profiles` (
  `profile_id` varchar(32) NOT NULL COMMENT '画像ID',
  `student_id` varchar(32) NOT NULL COMMENT '学生ID',
  `subject` varchar(50) NOT NULL COMMENT '学科',
  `learning_characteristics` json COMMENT '学习特征',
  `academic_performance` json COMMENT '学术表现',
  `knowledge_mastery` json COMMENT '知识掌握度',
  `learning_behavior` json COMMENT '学习行为',
  `engagement_level` decimal(3,2) DEFAULT 0.00 COMMENT '参与度',
  `attention_span` int DEFAULT 0 COMMENT '注意力持续时间（分钟）',
  `preferred_learning_style` enum('visual','auditory','kinesthetic','reading') COMMENT '偏好学习方式',
  `difficulty_preference` enum('low','moderate','moderate_to_high','high') COMMENT '难度偏好',
  `collaboration_tendency` decimal(3,2) DEFAULT 0.00 COMMENT '协作倾向',
  `self_regulation_ability` decimal(3,2) DEFAULT 0.00 COMMENT '自我调节能力',
  `motivation_level` decimal(3,2) DEFAULT 0.00 COMMENT '学习动机',
  `confidence_level` decimal(3,2) DEFAULT 0.00 COMMENT '自信水平',
  `risk_factors` json COMMENT '风险因素',
  `growth_potential` decimal(3,2) DEFAULT 0.00 COMMENT '成长潜力',
  `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`profile_id`),
  UNIQUE KEY `uk_student_subject` (`student_id`, `subject`),
  KEY `idx_engagement_level` (`engagement_level`),
  KEY `idx_learning_style` (`preferred_learning_style`),
  CONSTRAINT `fk_student_learning_profiles_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生学习画像表';

-- ==========================================
-- 8. 系统管理
-- ==========================================

-- 通知消息表
CREATE TABLE `notifications` (
  `notification_id` varchar(32) NOT NULL COMMENT '通知ID',
  `user_id` varchar(32) NOT NULL COMMENT '用户ID',
  `notification_type` enum('system','grade','homework','schedule','ai_insight','announcement') NOT NULL COMMENT '通知类型',
  `priority` enum('low','medium','high','urgent') NOT NULL DEFAULT 'medium' COMMENT '优先级',
  `title` varchar(200) NOT NULL COMMENT '标题',
  `content` text NOT NULL COMMENT '内容',
  `action_url` varchar(500) COMMENT '操作链接',
  `metadata` json COMMENT '元数据',
  `status` enum('unread','read','archived') NOT NULL DEFAULT 'unread' COMMENT '状态',
  `delivery_method` json COMMENT '推送方式',
  `scheduled_time` timestamp COMMENT '计划推送时间',
  `sent_time` timestamp COMMENT '实际推送时间',
  `read_time` timestamp COMMENT '阅读时间',
  `expires_at` timestamp COMMENT '过期时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`notification_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_notification_type` (`notification_type`),
  KEY `idx_priority` (`priority`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_notifications_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知消息表';

-- 文件管理表
CREATE TABLE `file_storage` (
  `file_id` varchar(32) NOT NULL COMMENT '文件ID',
  `user_id` varchar(32) NOT NULL COMMENT '上传用户ID',
  `file_name` varchar(255) NOT NULL COMMENT '文件名',
  `original_name` varchar(255) NOT NULL COMMENT '原始文件名',
  `file_type` enum('lesson_material','homework','exam_paper','image','video','audio','document','other') NOT NULL COMMENT '文件类型',
  `mime_type` varchar(100) NOT NULL COMMENT 'MIME类型',
  `file_size` bigint NOT NULL COMMENT '文件大小（字节）',
  `file_path` varchar(500) NOT NULL COMMENT '文件路径',
  `file_url` varchar(500) COMMENT '访问URL',
  `thumbnail_url` varchar(500) COMMENT '缩略图URL',
  `storage_provider` enum('local','oss','s3','cos') NOT NULL DEFAULT 'local' COMMENT '存储提供商',
  `category` varchar(50) COMMENT '分类',
  `tags` json COMMENT '标签',
  `metadata` json COMMENT '文件元数据',
  `ai_analysis` json COMMENT 'AI分析结果',
  `download_count` int DEFAULT 0 COMMENT '下载次数',
  `view_count` int DEFAULT 0 COMMENT '查看次数',
  `is_public` tinyint(1) DEFAULT 0 COMMENT '是否公开',
  `is_deleted` tinyint(1) DEFAULT 0 COMMENT '是否删除',
  `deleted_at` timestamp NULL COMMENT '删除时间',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`file_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_file_type` (`file_type`),
  KEY `idx_category` (`category`),
  KEY `idx_is_deleted` (`is_deleted`),
  CONSTRAINT `fk_file_storage_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件管理表';

-- 系统日志表
CREATE TABLE `system_logs` (
  `log_id` varchar(32) NOT NULL COMMENT '日志ID',
  `user_id` varchar(32) COMMENT '用户ID',
  `action` varchar(100) NOT NULL COMMENT '操作',
  `resource_type` varchar(50) COMMENT '资源类型',
  `resource_id` varchar(32) COMMENT '资源ID',
  `ip_address` varchar(45) COMMENT 'IP地址',
  `user_agent` text COMMENT '用户代理',
  `request_method` varchar(10) COMMENT '请求方法',
  `request_url` varchar(500) COMMENT '请求URL',
  `request_params` json COMMENT '请求参数',
  `response_status` int COMMENT '响应状态码',
  `response_time` int COMMENT '响应时间（毫秒）',
  `error_message` text COMMENT '错误信息',
  `session_id` varchar(64) COMMENT '会话ID',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`log_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_action` (`action`),
  KEY `idx_resource_type` (`resource_type`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_system_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志表';

-- ==========================================
-- 9. 索引优化建议
-- ==========================================

-- 复合索引建议
CREATE INDEX `idx_users_school_role_status` ON `users` (`school_id`, `role`, `status`);
CREATE INDEX `idx_grade_records_exam_score` ON `grade_records` (`exam_id`, `total_score` DESC);
CREATE INDEX `idx_classroom_sessions_teacher_date` ON `classroom_sessions` (`teacher_id`, `start_time`);
CREATE INDEX `idx_notifications_user_status_priority` ON `notifications` (`user_id`, `status`, `priority`);
CREATE INDEX `idx_ai_chat_messages_session_created` ON `ai_chat_messages` (`session_id`, `created_at`);

-- ==========================================
-- 10. 视图定义
-- ==========================================

-- 教师工作台统计视图
CREATE VIEW `teacher_dashboard_stats` AS
SELECT 
    u.user_id,
    u.real_name,
    COUNT(DISTINCT s.student_id) as student_count,
    COUNT(DISTINCT cs.session_id) as total_classes,
    COUNT(DISTINCT CASE WHEN cs.start_time >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN cs.session_id END) as weekly_classes,
    AVG(gr.total_score) as average_score,
    SUM(lp.preparation_time) as total_preparation_time
FROM users u
LEFT JOIN classes c ON u.user_id = c.head_teacher_id
LEFT JOIN students s ON c.class_id = s.class_id
LEFT JOIN classroom_sessions cs ON u.user_id = cs.teacher_id
LEFT JOIN lesson_preparations lp ON u.user_id = lp.teacher_id
LEFT JOIN exams e ON u.user_id = e.teacher_id
LEFT JOIN grade_records gr ON e.exam_id = gr.exam_id
WHERE u.role = 'teacher' AND u.status = 'active'
GROUP BY u.user_id, u.real_name;

-- 班级成绩统计视图
CREATE VIEW `class_grade_statistics` AS
SELECT 
    c.class_id,
    c.class_name,
    e.exam_id,
    e.exam_name,
    e.subject,
    COUNT(gr.record_id) as participant_count,
    AVG(gr.total_score) as average_score,
    MAX(gr.total_score) as max_score,
    MIN(gr.total_score) as min_score,
    STDDEV(gr.total_score) as std_deviation,
    COUNT(CASE WHEN gr.total_score >= e.pass_score THEN 1 END) / COUNT(gr.record_id) * 100 as pass_rate
FROM classes c
JOIN students s ON c.class_id = s.class_id
JOIN grade_records gr ON s.student_id = gr.student_id
JOIN exams e ON gr.exam_id = e.exam_id
WHERE s.status = 'active'
GROUP BY c.class_id, c.class_name, e.exam_id, e.exam_name, e.subject;

-- 学生学习进度视图
CREATE VIEW `student_learning_progress` AS
SELECT 
    s.student_id,
    s.student_name,
    c.class_name,
    COUNT(DISTINCT gr.exam_id) as exam_count,
    AVG(gr.total_score) as average_score,
    MAX(gr.total_score) as best_score,
    MIN(gr.total_score) as worst_score,
    COUNT(CASE WHEN gr.total_score >= e.pass_score THEN 1 END) / COUNT(gr.record_id) * 100 as pass_rate,
    CASE 
        WHEN AVG(gr.total_score) >= 90 THEN 'A'
        WHEN AVG(gr.total_score) >= 80 THEN 'B'
        WHEN AVG(gr.total_score) >= 70 THEN 'C'
        WHEN AVG(gr.total_score) >= 60 THEN 'D'
        ELSE 'F'
    END as overall_grade
FROM students s
JOIN classes c ON s.class_id = c.class_id
JOIN grade_records gr ON s.student_id = gr.student_id
JOIN exams e ON gr.exam_id = e.exam_id
WHERE s.status = 'active'
GROUP BY s.student_id, s.student_name, c.class_name;

-- ==========================================
-- 11. 存储过程示例
-- ==========================================

DELIMITER //

-- 计算班级排名的存储过程
CREATE PROCEDURE `CalculateClassRanking`(
    IN exam_id_param VARCHAR(32)
)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE student_id_var VARCHAR(32);
    DECLARE class_id_var VARCHAR(32);
    DECLARE total_score_var DECIMAL(6,2);
    DECLARE rank_var INT;
    
    DECLARE cur CURSOR FOR 
        SELECT gr.student_id, s.class_id, gr.total_score
        FROM grade_records gr
        JOIN students s ON gr.student_id = s.student_id
        WHERE gr.exam_id = exam_id_param
        ORDER BY s.class_id, gr.total_score DESC;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO student_id_var, class_id_var, total_score_var;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- 计算班级内排名
        SELECT COUNT(*) + 1 INTO rank_var
        FROM grade_records gr2
        JOIN students s2 ON gr2.student_id = s2.student_id
        WHERE gr2.exam_id = exam_id_param 
        AND s2.class_id = class_id_var 
        AND gr2.total_score > total_score_var;
        
        -- 更新排名
        UPDATE grade_records 
        SET rank_in_class = rank_var
        WHERE exam_id = exam_id_param AND student_id = student_id_var;
        
    END LOOP;
    
    CLOSE cur;
END //

DELIMITER ;

-- ==========================================
-- 12. 触发器示例
-- ==========================================

-- 用户创建时自动创建偏好设置
DELIMITER //
CREATE TRIGGER `after_user_insert` 
AFTER INSERT ON `users`
FOR EACH ROW
BEGIN
    INSERT INTO `user_preferences` (`user_id`) VALUES (NEW.user_id);
END //
DELIMITER ;

-- 成绩录入时自动更新统计信息
DELIMITER //
CREATE TRIGGER `after_grade_insert` 
AFTER INSERT ON `grade_records`
FOR EACH ROW
BEGIN
    -- 更新考试参与人数
    UPDATE `exams` 
    SET `updated_at` = CURRENT_TIMESTAMP 
    WHERE `exam_id` = NEW.exam_id;
    
    -- 可以在这里添加更多统计更新逻辑
END //
DELIMITER ;

-- ==========================================
-- 13. 数据初始化
-- ==========================================

-- 插入示例学校数据
INSERT INTO `schools` (`school_id`, `school_name`, `school_code`, `school_type`, `region`, `address`, `contact_phone`, `contact_email`, `principal_name`) VALUES
('school_001', '北京示例中学', 'BJSZ001', '高中', '北京市海淀区', '北京市海淀区中关村大街1号', '010-12345678', 'contact@bjsz.edu.cn', '张校长'),
('school_002', '上海实验高中', 'SHSY002', '高中', '上海市浦东新区', '上海市浦东新区世纪大道100号', '021-87654321', 'info@shsy.edu.cn', '李校长');

-- 插入示例管理员用户
INSERT INTO `users` (`user_id`, `username`, `password_hash`, `real_name`, `email`, `phone`, `role`, `status`, `school_id`, `employee_id`) VALUES
('admin_001', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9qK', '系统管理员', 'admin@system.com', '13800000000', 'super_admin', 'active', 'school_001', 'ADMIN001'),
('teacher_001', 'zhang_teacher', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9qK', '张老师', 'zhang@bjsz.edu.cn', '13800138000', 'teacher', 'active', 'school_001', 'T001');

-- 插入示例教师档案
INSERT INTO `teacher_profiles` (`user_id`, `subject`, `grade_levels`, `teaching_years`, `education_background`, `certification`, `specialties`) VALUES
('teacher_001', '生物', '["高一", "高二", "高三"]', 8, '生物学硕士', '高级教师资格证', '["分子生物学", "实验教学", "科研指导"]');

-- 插入示例班级数据
INSERT INTO `classes` (`class_id`, `class_name`, `grade`, `school_id`, `head_teacher_id`, `student_count`, `classroom`, `academic_year`, `semester`) VALUES
('class_001', '高一(1)班', '高一', 'school_001', 'teacher_001', 45, '教学楼A101', '2024-2025', 'autumn'),
('class_002', '高一(2)班', '高一', 'school_001', 'teacher_001', 43, '教学楼A102', '2024-2025', 'autumn');

-- 插入示例学生数据
INSERT INTO `students` (`student_id`, `student_name`, `student_number`, `class_id`, `gender`, `enrollment_date`) VALUES
('student_001', '王小明', '2024001001', 'class_001', 'male', '2024-09-01'),
('student_002', '李小红', '2024001002', 'class_001', 'female', '2024-09-01'),
('student_003', '张小华', '2024001003', 'class_002', 'male', '2024-09-01');

-- 插入示例课程数据
INSERT INTO `courses` (`course_id`, `course_name`, `course_code`, `subject`, `grade`, `semester`, `academic_year`, `teacher_id`, `class_ids`, `total_hours`, `weekly_hours`, `start_date`, `end_date`) VALUES
('course_001', '高中生物必修一', 'BIO_M1_2024', '生物', '高一', 'autumn', '2024-2025', 'teacher_001', '["class_001", "class_002"]', 72, 3, '2024-09-01', '2025-01-20');

-- ==========================================
-- 14. 性能优化建议
-- ==========================================

-- 分区表建议（针对大数据量表）
-- 系统日志表按月分区
/*
ALTER TABLE `system_logs` 
PARTITION BY RANGE (YEAR(created_at) * 100 + MONTH(created_at)) (
    PARTITION p202401 VALUES LESS THAN (202402),
    PARTITION p202402 VALUES LESS THAN (202403),
    PARTITION p202403 VALUES LESS THAN (202404),
    PARTITION p202404 VALUES LESS THAN (202405),
    PARTITION p202405 VALUES LESS THAN (202406),
    PARTITION p202406 VALUES LESS THAN (202407),
    PARTITION p202407 VALUES LESS THAN (202408),
    PARTITION p202408 VALUES LESS THAN (202409),
    PARTITION p202409 VALUES LESS THAN (202410),
    PARTITION p202410 VALUES LESS THAN (202411),
    PARTITION p202411 VALUES LESS THAN (202412),
    PARTITION p202412 VALUES LESS THAN (202501),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
*/

-- AI聊天消息表按年分区
/*
ALTER TABLE `ai_chat_messages` 
PARTITION BY RANGE (YEAR(created_at)) (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
*/

-- ==========================================
-- 15. 数据清理和维护
-- ==========================================

-- 定期清理过期通知的事件
/*
CREATE EVENT `cleanup_expired_notifications`
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
  DELETE FROM `notifications` 
  WHERE `expires_at` < NOW() 
  AND `status` = 'read';
*/

-- 定期清理旧的系统日志
/*
CREATE EVENT `cleanup_old_system_logs`
ON SCHEDULE EVERY 1 WEEK
STARTS CURRENT_TIMESTAMP
DO
  DELETE FROM `system_logs` 
  WHERE `created_at` < DATE_SUB(NOW(), INTERVAL 3 MONTH);
*/

-- ==========================================
-- 16. 备份和恢复建议
-- ==========================================

/*
备份策略建议：
1. 全量备份：每周一次
2. 增量备份：每日一次
3. 关键表实时备份：users, grade_records, classroom_sessions

备份命令示例：
mysqldump --single-transaction --routines --triggers \
  --databases intelligent_teaching_assistant > backup_$(date +%Y%m%d).sql

恢复命令示例：
mysql intelligent_teaching_assistant < backup_20241215.sql
*/

-- ==========================================
-- 17. 监控和告警
-- ==========================================

/*
监控指标建议：
1. 连接数监控
2. 慢查询监控
3. 表空间使用率
4. 主从复制延迟
5. 死锁监控

告警阈值建议：
- 连接数 > 80%
- 慢查询 > 100/小时
- 表空间使用率 > 85%
- 复制延迟 > 10秒
*/

-- ==========================================
-- 18. 安全配置建议
-- ==========================================

/*
安全配置建议：
1. 启用SSL连接
2. 设置复杂密码策略
3. 限制远程访问IP
4. 定期更新用户密码
5. 启用审计日志
6. 数据加密存储

用户权限建议：
- 应用用户：只授予必要的DML权限
- 只读用户：只授予SELECT权限
- 备份用户：只授予备份相关权限
- 管理用户：完整权限但限制访问IP
*/

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- ==========================================
-- 文档结束
-- ==========================================

/*
数据库设计说明：

1. 字符集：使用utf8mb4支持完整的Unicode字符集
2. 存储引擎：使用InnoDB支持事务和外键约束
3. 主键：统一使用varchar(32)作为主键，便于分布式扩展
4. 时间戳：统一使用timestamp类型，自动维护创建和更新时间
5. JSON字段：用于存储复杂的结构化数据，提高灵活性
6. 索引策略：基于查询模式设计复合索引，提高查询性能
7. 外键约束：保证数据完整性，使用适当的级联操作
8. 分区策略：对大数据量表使用分区提高查询性能
9. 视图设计：提供常用的统计查询视图，简化应用层开发
10. 存储过程：封装复杂的业务逻辑，提高执行效率

版本历史：
v2.0.0 - 2024-12-15 - 初始版本，包含完整的智能教学助手数据库设计

维护说明：
- 定期检查和优化索引
- 监控表空间使用情况
- 定期清理历史数据
- 保持统计信息更新
- 定期备份重要数据
*/
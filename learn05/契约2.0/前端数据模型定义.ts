/**
 * 智能教学助手2.0 前端数据模型定义
 * 
 * 本文件定义了前端应用中使用的所有数据模型和接口类型
 * 与后端API契约保持一致，确保类型安全
 * 
 * @version 2.0.0
 * @date 2024-12-15
 */

// ==================== 基础类型定义 ====================

/** 通用响应格式 */
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
  timestamp: string;
  request_id: string;
}

/** 分页信息 */
export interface Pagination {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

/** 分页响应数据 */
export interface PaginatedResponse<T> {
  items: T[];
  pagination: Pagination;
}

/** 错误详情 */
export interface ErrorDetail {
  field: string;
  message: string;
  code: string;
}

/** 错误响应 */
export interface ErrorResponse {
  error_code: string;
  error_type: string;
  details: ErrorDetail[];
  request_id: string;
  timestamp: string;
}

// ==================== 用户相关模型 ====================

/** 用户角色 */
export type UserRole = 'teacher' | 'student' | 'admin';

/** 用户状态 */
export type UserStatus = 'active' | 'inactive' | 'suspended';

/** 学校信息 */
export interface SchoolInfo {
  school_id: string;
  school_name: string;
  school_code: string;
  school_type: string;
  region: string;
}

/** 教学档案 */
export interface TeachingProfile {
  subject: string;
  grade_levels: string[];
  teaching_years: number;
  certification: string;
  specialties: string[];
}

/** 用户偏好设置 */
export interface UserPreferences {
  theme: 'light' | 'dark';
  language: string;
  notification_settings: {
    email: boolean;
    sms: boolean;
    push: boolean;
  };
}

/** 用户信息 */
export interface User {
  user_id: string;
  username: string;
  real_name: string;
  email: string;
  phone: string;
  avatar: string;
  role: UserRole;
  status: UserStatus;
  last_login: string;
  created_at: string;
  school_info: SchoolInfo;
  teaching_profile?: TeachingProfile;
  preferences: UserPreferences;
}

/** 登录请求 */
export interface LoginRequest {
  username: string;
  password: string;
  login_type: 'password' | 'sms' | 'wechat';
  device_info: {
    device_id: string;
    device_type: 'web' | 'ios' | 'android';
    user_agent: string;
  };
}

/** 登录响应 */
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user_info: User;
}

// ==================== 工作台相关模型 ====================

/** 趋势数据 */
export interface TrendData {
  value: number;
  percentage: number;
  direction: 'up' | 'down' | 'stable';
  period: string;
}

/** 统计数据项 */
export interface StatItem {
  total: number;
  trend: TrendData;
}

/** 工作台统计数据 */
export interface DashboardStats {
  student_count: StatItem;
  course_count: StatItem;
  average_score: StatItem;
  preparation_hours: StatItem;
}

/** 快速操作 */
export interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'error';
  url: string;
  enabled: boolean;
}

/** 工作台概览数据 */
export interface DashboardOverview {
  stats: DashboardStats;
  quick_actions: QuickAction[];
}

/** 活动类型 */
export type ActivityType = 'lesson_create' | 'homework_grade' | 'experiment_design' | 'grade_analysis';

/** 活动记录 */
export interface Activity {
  id: string;
  type: ActivityType;
  title: string;
  description: string;
  icon: string;
  color: string;
  created_at: string;
  relative_time: string;
  metadata: Record<string, any>;
}

/** 课程状态 */
export type ScheduleStatus = 'upcoming' | 'current' | 'completed' | 'cancelled';

/** 课程操作 */
export interface ScheduleAction {
  type: string;
  label: string;
  url: string;
  primary: boolean;
}

/** 班级信息 */
export interface ClassInfo {
  class_id: string;
  class_name: string;
  student_count: number;
  classroom: string;
}

/** 课程信息 */
export interface LessonInfo {
  lesson_id: string;
  chapter: string;
  section: string;
  preparation_status: 'draft' | 'completed';
  has_courseware: boolean;
  has_experiment: boolean;
}

/** 课程安排 */
export interface ScheduleItem {
  id: string;
  start_time: string;
  end_time: string;
  duration: number;
  subject: string;
  topic: string;
  class_info: ClassInfo;
  lesson_info: LessonInfo;
  status: ScheduleStatus;
  actions: ScheduleAction[];
}

/** 今日课程安排 */
export interface DailySchedule {
  date: string;
  day_of_week: string;
  total_classes: number;
  current_class?: {
    class_id: string;
    is_current: boolean;
    time_remaining: number;
  };
  classes: ScheduleItem[];
}

// ==================== 备课助手相关模型 ====================

/** 教材信息 */
export interface TextbookInfo {
  publisher: string;
  subject: string;
  grade: string;
  volume: string;
  edition: string;
  chapter?: string;
  section?: string;
  title?: string;
}

/** 知识点级别 */
export type KnowledgePointLevel = 'core' | 'important' | 'general';

/** 知识点 */
export interface KnowledgePoint {
  id: string;
  name: string;
  level: KnowledgePointLevel;
  difficulty: number; // 1-5级难度
  description: string;
  prerequisites: string[];
  related_concepts: string[];
}

/** 认知水平分布 */
export interface CognitiveLevels {
  remember: number;
  understand: number;
  apply: number;
  analyze: number;
}

/** 挑战点 */
export interface ChallengingPoint {
  point: string;
  reason: string;
  suggestions: string[];
}

/** 难度分析 */
export interface DifficultyAnalysis {
  overall_difficulty: number;
  cognitive_levels: CognitiveLevels;
  challenging_points: ChallengingPoint[];
}

/** 教学目标 */
export interface TeachingObjectives {
  knowledge_objectives: string[];
  ability_objectives: string[];
  emotion_objectives: string[];
}

/** 教学方法 */
export interface TeachingMethod {
  method: string;
  description: string;
  applicable_points: string[];
}

/** 教学资源 */
export interface TeachingResource {
  type: 'animation' | 'image' | 'video' | 'document';
  title: string;
  url: string;
  duration?: number;
  description?: string;
}

/** 教学建议 */
export interface TeachingSuggestions {
  key_points: string[];
  difficult_points: string[];
  teaching_methods: TeachingMethod[];
  resources: TeachingResource[];
}

/** 实验推荐 */
export interface ExperimentRecommendation {
  id: string;
  title: string;
  type: 'demonstration' | 'group' | 'individual';
  difficulty: number;
  duration: number;
  materials: string[];
  procedure: string[];
  expected_results: string;
  safety_notes: string[];
}

/** 评估建议 */
export interface AssessmentSuggestions {
  formative_assessment: string[];
  summative_assessment: string[];
}

/** 教材分析结果 */
export interface TextbookAnalysis {
  analysis_id: string;
  textbook_info: TextbookInfo;
  knowledge_points: KnowledgePoint[];
  difficulty_analysis: DifficultyAnalysis;
  teaching_objectives: TeachingObjectives;
  teaching_suggestions: TeachingSuggestions;
  experiment_recommendations: ExperimentRecommendation[];
  assessment_suggestions: AssessmentSuggestions;
  ai_confidence: number;
  analysis_time: string;
}

/** 教学活动 */
export interface TeachingActivity {
  type: 'question' | 'explanation' | 'multimedia' | 'group_discussion' | 'demonstration' | 'exercise' | 'quiz' | 'summary' | 'homework';
  content: string;
  duration: number;
  interaction_type?: string;
  resource_url?: string;
  key_points?: string[];
  visual_aids?: string[];
  group_size?: number;
  discussion_points?: string[];
  materials?: string[];
  assessment_criteria?: string[];
  question_count?: number;
  estimated_time?: number;
}

/** 教学阶段 */
export interface TeachingPhase {
  phase: string;
  duration: number;
  objectives: string[];
  activities: TeachingActivity[];
  teaching_tips?: string[];
}

/** 课程结构 */
export interface LessonStructure {
  phases: TeachingPhase[];
}

/** 评估计划 */
export interface AssessmentPlan {
  formative_assessment: Array<{
    method: string;
    focus: string;
    timing: string;
  }>;
  summative_assessment: Array<{
    method: string;
    scoring_criteria: string;
    timing: string;
  }>;
}

/** 差异化策略 */
export interface DifferentiationStrategies {
  for_advanced_students: string[];
  for_struggling_students: string[];
}

/** 潜在挑战 */
export interface PotentialChallenge {
  challenge: string;
  solution: string;
  prevention: string;
}

/** 教学计划 */
export interface LessonPlan {
  lesson_plan_id: string;
  lesson_info: {
    subject: string;
    grade: string;
    topic: string;
    duration: number;
    estimated_preparation_time: number;
  };
  lesson_structure: LessonStructure;
  resources_needed: Array<{
    type: string;
    name: string;
    url?: string;
    quantity?: number | string;
    usage_time: string;
    preparation_note?: string;
  }>;
  assessment_plan: AssessmentPlan;
  differentiation_strategies: DifferentiationStrategies;
  potential_challenges: PotentialChallenge[];
  ai_suggestions: string[];
  confidence_score: number;
  generated_at: string;
}

// ==================== 课堂AI助手相关模型 ====================

/** 问题类型 */
export type QuestionType = 'multiple_choice' | 'short_answer' | 'essay';

/** 认知水平 */
export type CognitiveLevel = 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create';

/** 学习状态 */
export type LearningState = 'on_track' | 'struggling' | 'advanced' | 'disengaged';

/** 问题数据 */
export interface QuestionData {
  question_id: string;
  question_text: string;
  question_type: QuestionType;
  knowledge_points: string[];
  difficulty_level: number;
  cognitive_level: CognitiveLevel;
}

/** 学生回答 */
export interface StudentResponse {
  student_id: string;
  response: string;
  response_time: number;
  confidence_level: number;
  submission_time: string;
}

/** 学情分析上下文 */
export interface AnalysisContext {
  lesson_topic: string;
  current_phase: string;
  previous_questions: string[];
}

/** 常见错误 */
export interface CommonError {
  error_type: string;
  count: number;
  description: string;
  suggested_intervention: string;
}

/** 问题分析结果 */
export interface QuestionAnalysis {
  question_id: string;
  total_responses: number;
  response_rate: number;
  average_response_time: number;
  correctness_distribution: {
    correct: number;
    partially_correct: number;
    incorrect: number;
  };
  common_errors: CommonError[];
}

/** 知识掌握度 */
export interface KnowledgeMastery {
  [knowledge_point: string]: number;
}

/** 个人分析结果 */
export interface IndividualAnalysis {
  student_id: string;
  correctness: number;
  response_quality: 'excellent' | 'good' | 'average' | 'needs_improvement';
  knowledge_mastery: KnowledgeMastery;
  learning_state: LearningState;
  confidence_match: boolean;
  attention_level: number;
}

/** 知识缺口 */
export interface KnowledgeGap {
  concept: string;
  gap_percentage: number;
  priority: 'high' | 'medium' | 'low';
}

/** 注意力分布 */
export interface AttentionDistribution {
  high: number;
  medium: number;
  low: number;
}

/** 班级洞察 */
export interface ClassInsights {
  overall_understanding: number;
  engagement_level: number;
  difficulty_perception: 'too_easy' | 'appropriate' | 'too_hard';
  knowledge_gaps: KnowledgeGap[];
  learning_pace: 'slow' | 'normal' | 'fast';
  attention_distribution: AttentionDistribution;
}

/** 即时行动建议 */
export interface ImmediateAction {
  type: 'clarification' | 'review' | 'practice' | 'break';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  description: string;
  target_students?: string[];
  estimated_time: number;
}

/** 下一题建议 */
export interface NextQuestionSuggestion {
  question_type: QuestionType;
  focus: string;
  difficulty_adjustment: -1 | 0 | 1;
  reason: string;
}

/** 教学调整建议 */
export interface TeachingAdjustment {
  adjustment: string;
  reason: string;
  implementation: string;
}

/** 学情分析建议 */
export interface LearningStateRecommendations {
  immediate_actions: ImmediateAction[];
  next_question_suggestions: NextQuestionSuggestion[];
  teaching_adjustments: TeachingAdjustment[];
}

/** 学情分析结果 */
export interface LearningStateAnalysis {
  analysis_id: string;
  session_id: string;
  question_analysis: QuestionAnalysis;
  individual_analysis: IndividualAnalysis[];
  class_insights: ClassInsights;
  recommendations: LearningStateRecommendations;
  confidence_score: number;
  analysis_time: string;
}

// ==================== 实验设计相关模型 ====================

/** 实验类型 */
export type ExperimentType = 'demonstration' | 'group' | 'individual';

/** 安全等级 */
export type SafetyLevel = 'basic' | 'intermediate' | 'advanced';

/** 实验室条件 */
export interface LabConditions {
  has_microscopes: boolean;
  microscope_count: number;
  has_centrifuge: boolean;
  safety_level: SafetyLevel;
}

/** 实验需求 */
export interface ExperimentRequirements {
  topic: string;
  grade_level: string;
  student_count: number;
  duration: number;
  lab_conditions: LabConditions;
  learning_objectives: string[];
  available_materials: string[];
}

/** 实验偏好 */
export interface ExperimentPreferences {
  experiment_type: ExperimentType;
  safety_priority: 'low' | 'medium' | 'high';
  include_variations: boolean;
}

/** 材料清单项 */
export interface MaterialItem {
  name: string;
  quantity: number | string;
  specification?: string;
  note?: string;
  preparation?: string;
}

/** 材料清单 */
export interface MaterialsList {
  per_group: MaterialItem[];
  shared_materials: MaterialItem[];
}

/** 实验步骤 */
export interface ExperimentStep {
  step: number;
  description: string;
  time: number;
  safety_notes?: string[];
  tips?: string[];
  technique?: string;
  importance?: string;
  organization?: string;
  reference?: string;
  expected_phenomenon?: string;
  observation_interval?: string;
  comparison?: string;
  observation_points?: string[];
}

/** 实验程序 */
export interface ExperimentProcedure {
  procedure_name: string;
  duration: number;
  steps: ExperimentStep[];
}

/** 实验阶段 */
export interface ExperimentPhase {
  duration: number;
  steps?: ExperimentStep[];
  procedures?: ExperimentProcedure[];
  activities?: Array<{
    activity: string;
    time: number;
    requirements?: string[];
    discussion_points?: string[];
    conclusion_framework?: string;
  }>;
}

/** 实验流程 */
export interface ExperimentalProcedure {
  preparation_phase: ExperimentPhase;
  main_experiment: ExperimentPhase;
  data_analysis: ExperimentPhase;
}

/** 安全指南 */
export interface SafetyGuideline {
  category: string;
  guidelines: string[];
}

/** 评估标准 */
export interface AssessmentCriteria {
  [category: string]: {
    weight: number;
    criteria: string[];
  };
}

/** 故障排除 */
export interface Troubleshooting {
  problem: string;
  possible_causes: string[];
  solutions: string[];
}

/** 扩展活动 */
export interface ExtensionActivity {
  activity: string;
  description: string;
  difficulty: 'basic' | 'intermediate' | 'advanced';
}

/** 实验设计方案 */
export interface ExperimentDesign {
  experiment_id: string;
  basic_info: {
    title: string;
    type: string;
    difficulty_level: number;
    estimated_duration: number;
    group_size: number;
    group_count: number;
  };
  learning_objectives: {
    knowledge_objectives: string[];
    skill_objectives: string[];
    attitude_objectives: string[];
  };
  materials_list: MaterialsList;
  experimental_procedure: ExperimentalProcedure;
  safety_guidelines: SafetyGuideline[];
  assessment_criteria: AssessmentCriteria;
  troubleshooting: Troubleshooting[];
  extension_activities: ExtensionActivity[];
  ai_optimization_suggestions: string[];
  confidence_score: number;
  generated_at: string;
}

// ==================== 成绩管理相关模型 ====================

/** 考试类型 */
export type ExamType = 'quiz' | 'midterm' | 'final' | 'homework';

/** 导入类型 */
export type ImportType = 'excel' | 'manual' | 'ocr' | 'voice';

/** 考试信息 */
export interface ExamInfo {
  exam_name: string;
  exam_type: ExamType;
  subject: string;
  exam_date: string;
  full_score: number;
  class_ids: string[];
}

/** 分数详情 */
export interface ScoreDetails {
  [section: string]: number;
}

/** 成绩数据 */
export interface GradeData {
  student_id: string;
  student_name: string;
  class_id: string;
  total_score: number;
  section_scores: ScoreDetails;
  knowledge_point_scores: KnowledgeMastery;
}

/** 验证选项 */
export interface ValidationOptions {
  check_duplicates: boolean;
  validate_score_range: boolean;
  auto_correct: boolean;
}

/** 导入请求 */
export interface GradeImportRequest {
  import_type: ImportType;
  exam_info: ExamInfo;
  grade_data: GradeData[];
  validation_options: ValidationOptions;
}

/** 导入记录 */
export interface ImportRecord {
  student_id: string;
  student_name: string;
  total_score?: number;
  status: 'imported' | 'failed';
  error_type?: string;
  error_message?: string;
  suggested_action?: string;
}

/** 验证警告 */
export interface ValidationWarning {
  student_id: string;
  warning_type: string;
  warning_message: string;
  current_score: number;
  historical_average: number;
}

/** 导入详情 */
export interface ImportDetails {
  successful_records: ImportRecord[];
  failed_records: ImportRecord[];
  validation_warnings: ValidationWarning[];
}

/** 班级统计 */
export interface ClassStatistics {
  average: number;
  median: number;
  std_deviation: number;
  pass_rate: number;
}

/** 科目分析 */
export interface SubjectAnalysis {
  overall_difficulty: 'easy' | 'moderate' | 'hard';
  challenging_topics: string[];
  well_mastered_topics: string[];
}

/** 自动分析结果 */
export interface AutoAnalysis {
  class_statistics: { [class_id: string]: ClassStatistics };
  subject_analysis: SubjectAnalysis;
}

/** 后续步骤 */
export interface NextStep {
  action: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
}

/** 导入摘要 */
export interface ImportSummary {
  total_records: number;
  successful_imports: number;
  failed_imports: number;
  duplicate_records: number;
  validation_errors: number;
}

/** 成绩导入结果 */
export interface GradeImportResult {
  import_id: string;
  import_summary: ImportSummary;
  import_details: ImportDetails;
  auto_analysis: AutoAnalysis;
  next_steps: NextStep[];
  imported_at: string;
}

/** 描述性统计 */
export interface DescriptiveStats {
  mean: number;
  median: number;
  mode: number;
  std_deviation: number;
  variance: number;
  min: number;
  max: number;
  range: number;
  quartiles: {
    q1: number;
    q2: number;
    q3: number;
    iqr: number;
  };
}

/** 分布区间 */
export interface DistributionRange {
  range: string;
  count: number;
  percentage: number;
}

/** 正态性检验 */
export interface NormalityTest {
  test_statistic: number;
  p_value: number;
  is_normal: boolean;
  interpretation: string;
}

/** 分布分析 */
export interface DistributionAnalysis {
  histogram_data: DistributionRange[];
  normality_test: NormalityTest;
  skewness: number;
  kurtosis: number;
  distribution_shape: string;
}

/** 表现水平 */
export interface PerformanceLevel {
  range: string;
  count: number;
  percentage: number;
}

/** 整体统计 */
export interface OverallStatistics {
  descriptive_stats: DescriptiveStats;
  distribution_analysis: DistributionAnalysis;
  performance_levels: { [level: string]: PerformanceLevel };
}

/** 班级对比 */
export interface ClassComparison {
  [class_id: string]: {
    class_name: string;
    student_count: number;
    average: number;
    pass_rate: number;
    rank: number;
    strengths: string[];
    weaknesses: string[];
  };
}

/** 知识点分析 */
export interface KnowledgePointAnalysis {
  [knowledge_point: string]: {
    average_score: number;
    difficulty_level: 'easy' | 'moderate' | 'hard';
    mastery_rate: number;
    common_errors: string[];
    improvement_suggestions: string[];
  };
}

/** 个人洞察 */
export interface IndividualInsight {
  student_id: string;
  student_name: string;
  total_score: number;
  rank: number;
  percentile: number;
  performance_trend: 'improving' | 'stable' | 'declining';
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  learning_style: string;
  attention_points: string[];
}

/** 推荐行动 */
export interface RecommendedAction {
  priority: 'low' | 'medium' | 'high';
  action: string;
  reason: string;
  implementation: string;
  target_students?: string[];
}

/** AI洞察 */
export interface AIInsights {
  overall_assessment: string;
  teaching_effectiveness: number;
  curriculum_coverage: number;
  recommended_actions: RecommendedAction[];
  future_focus: string[];
}

/** 成绩分析结果 */
export interface GradeAnalysis {
  analysis_id: string;
  exam_info: {
    exam_id: string;
    exam_name: string;
    subject: string;
    exam_date: string;
    total_participants: number;
  };
  overall_statistics: OverallStatistics;
  class_comparison: ClassComparison;
  knowledge_point_analysis: KnowledgePointAnalysis;
  individual_insights: IndividualInsight[];
  ai_insights: AIInsights;
  generated_at: string;
}

// ==================== 个性化学习建议相关模型 ====================

/** 学习特征 */
export interface LearningCharacteristics {
  learning_style: 'visual' | 'auditory' | 'kinesthetic' | 'reading';
  learning_pace: 'slow' | 'moderate' | 'fast';
  attention_span: 'short' | 'average' | 'long';
  preferred_difficulty: 'low' | 'moderate' | 'moderate_to_high' | 'high';
}

/** 学术表现 */
export interface AcademicPerformance {
  overall_grade: string;
  subject_ranking: number;
  class_ranking: number;
  trend: 'improving' | 'stable' | 'declining';
}

/** 学生档案 */
export interface StudentProfile {
  student_id: string;
  student_name: string;
  class_info: {
    class_id: string;
    class_name: string;
  };
  learning_characteristics: LearningCharacteristics;
  academic_performance: AcademicPerformance;
}

/** 掌握度项目 */
export interface MasteryItem {
  topic: string;
  mastery_level: number;
  confidence: 'low' | 'medium' | 'high';
  last_assessment: string;
  error_patterns?: string[];
  improvement_priority?: 'low' | 'medium' | 'high';
}

/** 知识掌握图谱 */
export interface KnowledgeMasteryMap {
  强项知识点: MasteryItem[];
  薄弱知识点: MasteryItem[];
}

/** 每日任务 */
export interface DailyTask {
  day: string;
  task: string;
  duration: number;
  resources: string[];
}

/** 周计划 */
export interface WeeklyPlan {
  week: number;
  focus_topic: string;
  daily_tasks: DailyTask[];
  week_goal: string;
  assessment: string;
}

/** 里程碑检查点 */
export interface MilestoneCheckpoint {
  checkpoint: string;
  target: string;
  assessment_method: string;
}

/** 个性化学习计划 */
export interface PersonalizedStudyPlan {
  plan_duration: string;
  weekly_schedule: WeeklyPlan[];
  milestone_checkpoints: MilestoneCheckpoint[];
}

/** 资源推荐 */
export interface ResourceRecommendation {
  title: string;
  url?: string;
  type?: string;
  duration?: number;
  difficulty?: string;
  relevance_score?: number;
  question_count?: number;
  difficulty_range?: string;
  estimated_time?: number;
  pages?: number;
  focus_areas?: string[];
}

/** 资源推荐集合 */
export interface ResourceRecommendations {
  视频资源: ResourceRecommendation[];
  练习资源: ResourceRecommendation[];
  参考资料: ResourceRecommendation[];
}

/** 适应性策略 */
export interface AdaptiveStrategies {
  学习方法建议: string[];
  时间管理建议: string[];
  心理调适建议: string[];
}

/** 进度跟踪 */
export interface ProgressTracking {
  tracking_metrics: string[];
  feedback_schedule: {
    daily: string;
    weekly: string;
    monthly: string;
  };
}

/** 个性化建议响应 */
export interface PersonalizedSuggestions {
  student_profile: StudentProfile;
  knowledge_mastery_map: KnowledgeMasteryMap;
  personalized_study_plan: PersonalizedStudyPlan;
  resource_recommendations: ResourceRecommendations;
  adaptive_strategies: AdaptiveStrategies;
  progress_tracking: ProgressTracking;
  ai_coaching_tips: string[];
  generated_at: string;
}

// ==================== AI问答相关模型 ====================

/** 消息类型 */
export type MessageType = 'text' | 'image' | 'voice';

/** 用户级别 */
export type UserLevel = 'student' | 'teacher';

/** 回答风格 */
export type ResponseStyle = 'simple' | 'detailed' | 'interactive';

/** 消息上下文 */
export interface MessageContext {
  subject: string;
  grade: string;
  topic: string;
  user_level: UserLevel;
}

/** 消息内容 */
export interface MessageContent {
  content: string;
  type: MessageType;
  context: MessageContext;
}

/** 回答偏好 */
export interface ResponsePreferences {
  response_style: ResponseStyle;
  include_examples: boolean;
  include_diagrams: boolean;
  language_level: string;
}

/** AI聊天请求 */
export interface AIChatRequest {
  session_id: string;
  message: MessageContent;
  preferences: ResponsePreferences;
}

/** 示例 */
export interface Example {
  title: string;
  description: string;
  relevance: string;
}

/** 视觉辅助 */
export interface VisualAid {
  type: 'diagram' | 'image' | 'animation' | 'video';
  title: string;
  url: string;
  description: string;
}

/** 回答内容 */
export interface AnswerContent {
  main_content: string;
  key_points: string[];
  examples: Example[];
  visual_aids: VisualAid[];
}

/** AI聊天响应 */
export interface AIChatResponse {
  response_id: string;
  session_id: string;
  answer: AnswerContent;
  related_questions: string[];
  learning_suggestions: string[];
  confidence_score: number;
  response_time: number;
  generated_at: string;
}

// ==================== 通知相关模型 ====================

/** 通知类型 */
export type NotificationType = 'system' | 'grade' | 'homework' | 'schedule' | 'ai_insight';

/** 通知优先级 */
export type NotificationPriority = 'low' | 'medium' | 'high' | 'urgent';

/** 通知状态 */
export type NotificationStatus = 'unread' | 'read';

/** 通知 */
export interface Notification {
  id: string;
  type: NotificationType;
  priority: NotificationPriority;
  title: string;
  content: string;
  status: NotificationStatus;
  created_at: string;
  action_url?: string;
  metadata: Record<string, any>;
}

/** 通知列表响应 */
export interface NotificationListResponse {
  unread_count: number;
  items: Notification[];
  pagination: Pagination;
}

// ==================== 文件管理相关模型 ====================

/** 文件类型 */
export type FileType = 'lesson_material' | 'homework' | 'exam_paper' | 'image' | 'video';

/** 文件元数据 */
export interface FileMetadata {
  subject: string;
  grade: string;
  chapter: string;
  tags: string[];
}

/** 文件上传请求 */
export interface FileUploadRequest {
  file_type: FileType;
  category: string;
  metadata: FileMetadata;
}

/** AI文件分析 */
export interface AIFileAnalysis {
  content_summary: string;
  slide_count?: number;
  estimated_duration?: number;
  key_topics: string[];
}

/** 文件上传响应 */
export interface FileUploadResponse {
  file_id: string;
  file_name: string;
  file_size: number;
  file_type: string;
  file_url: string;
  thumbnail_url?: string;
  upload_time: string;
  ai_analysis?: AIFileAnalysis;
}

// ==================== 说明 ====================

/**
 * 所有类型定义已通过 export interface 和 export type 直接导出
 * 无需额外的 export type 声明
 * 
 * 使用方式：
 * import { User, ApiResponse, DashboardStats } from './前端数据模型定义';
 */
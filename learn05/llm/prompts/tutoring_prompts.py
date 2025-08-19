# -*- coding: utf-8 -*-
"""
辅导方案相关提示词模板
包含个性化辅导、练习推荐、学习计划制定等功能
"""

from .base_prompts import BasePromptTemplate, PromptTemplate, PromptType

class TutoringPrompts(BasePromptTemplate):
    """辅导方案提示词模板类"""
    
    def _load_templates(self):
        """加载辅导方案相关的提示词模板"""
        
        # 个性化辅导方案生成模板
        self.templates["personalized_tutoring_plan"] = PromptTemplate(
            name="personalized_tutoring_plan",
            description="生成个性化的学习辅导方案",
            template="""你是一位资深的个性化教育专家，请为学生制定详细的辅导方案：

【学生基本信息】
姓名：{student_name}
年级：{grade}
科目：{subject}
当前水平：{current_level}

【学情分析结果】
{learning_analysis}

【薄弱环节】
{weak_points}

【学习目标】
短期目标：{short_term_goals}
长期目标：{long_term_goals}

【可用时间】
每周学习时间：{weekly_hours}小时
辅导周期：{tutoring_period}

【学习偏好】
{learning_preferences}

请制定包含以下要素的个性化辅导方案：

1. **辅导目标设定**
   - 具体的知识目标
   - 能力提升目标
   - 习惯养成目标
   - 可测量的成果指标

2. **内容规划**
   - 知识点梳理和补强
   - 技能训练重点
   - 思维方法培养
   - 学习策略指导

3. **阶段性安排**
   - 第一阶段（基础巩固）：时间、内容、目标
   - 第二阶段（能力提升）：时间、内容、目标
   - 第三阶段（综合应用）：时间、内容、目标
   - 各阶段的评估标准

4. **具体实施计划**
   - 每周学习安排
   - 每日学习任务
   - 重点难点突破策略
   - 练习和作业安排

5. **教学方法选择**
   - 适合的教学方式
   - 学习工具和资源
   - 互动和反馈机制
   - 激励和评价方式

6. **进度监控机制**
   - 学习进度跟踪方法
   - 阶段性评估安排
   - 调整和优化机制
   - 家长沟通计划

7. **预期效果和风险**
   - 预期学习成果
   - 可能遇到的困难
   - 风险防控措施
   - 应急调整方案

请确保方案具有针对性、可操作性和实效性。""",
            variables=["student_name", "grade", "subject", "current_level", "learning_analysis", "weak_points", "short_term_goals", "long_term_goals", "weekly_hours", "tutoring_period", "learning_preferences"],
            prompt_type=PromptType.USER,
            category="tutoring_plan",
            tags=["个性化辅导", "学习方案", "目标设定"]
        )
        
        # 练习题推荐模板
        self.templates["exercise_recommendation"] = PromptTemplate(
            name="exercise_recommendation",
            description="根据学生情况推荐合适的练习题",
            template="""你是一位练习题推荐专家，请为学生推荐合适的练习题：

【学生信息】
姓名：{student_name}
年级：{grade}
科目：{subject}
当前水平：{current_level}

【学习目标】
{learning_objectives}

【薄弱知识点】
{weak_knowledge_points}

【已掌握知识点】
{mastered_knowledge_points}

【练习需求】
练习类型：{exercise_types}
难度要求：{difficulty_level}
数量要求：{quantity_requirement}
时间限制：{time_limit}

【学习特点】
{learning_characteristics}

请按照以下要求推荐练习题：

1. **基础巩固练习**
   - 针对薄弱知识点的基础题
   - 概念理解和记忆强化题
   - 基本技能训练题
   - 推荐数量：{basic_quantity}道

2. **能力提升练习**
   - 综合应用题
   - 分析推理题
   - 创新思维题
   - 推荐数量：{advanced_quantity}道

3. **专项突破练习**
   - 针对特定难点的专项题
   - 易错题型的强化训练
   - 解题方法的专门练习
   - 推荐数量：{special_quantity}道

4. **综合测试练习**
   - 模拟考试题
   - 综合能力检测题
   - 时间管理训练题
   - 推荐数量：{test_quantity}套

5. **练习安排建议**
   - 每日练习计划
   - 练习顺序安排
   - 时间分配建议
   - 复习巩固计划

6. **练习方法指导**
   - 做题前的准备工作
   - 做题过程中的注意事项
   - 做题后的总结反思
   - 错题处理方法

7. **效果评估标准**
   - 正确率目标
   - 速度提升目标
   - 方法掌握程度
   - 进步评价指标

请提供具体的题目推荐和详细的练习指导。""",
            variables=["student_name", "grade", "subject", "current_level", "learning_objectives", "weak_knowledge_points", "mastered_knowledge_points", "exercise_types", "difficulty_level", "quantity_requirement", "time_limit", "learning_characteristics", "basic_quantity", "advanced_quantity", "special_quantity", "test_quantity"],
            prompt_type=PromptType.USER,
            category="exercise_recommendation",
            tags=["练习推荐", "题目选择", "能力训练"]
        )
        
        # 学习计划制定模板
        self.templates["study_schedule_planning"] = PromptTemplate(
            name="study_schedule_planning",
            description="制定详细的学习时间安排和计划",
            template="""你是一位学习规划专家，请为学生制定详细的学习计划：

【学生信息】
姓名：{student_name}
年级：{grade}
学习科目：{subjects}

【时间资源】
每日可用学习时间：{daily_study_time}小时
周末额外时间：{weekend_extra_time}小时
计划周期：{planning_period}

【学习目标】
{learning_goals}

【当前学习状况】
{current_status}

【重点关注科目】
{priority_subjects}

【学习习惯和偏好】
{study_habits}

【外部约束条件】
{constraints}

请制定包含以下内容的学习计划：

1. **总体时间分配**
   - 各科目时间分配比例
   - 学习与休息时间安排
   - 复习与预习时间分配
   - 练习与总结时间安排

2. **每日学习安排**
   - 早晨学习时段安排
   - 下午学习时段安排
   - 晚上学习时段安排
   - 碎片时间利用建议

3. **每周学习计划**
   - 周一至周五的详细安排
   - 周末的学习安排
   - 每周重点任务
   - 每周复习总结时间

4. **月度学习规划**
   - 月度学习目标
   - 重要节点和里程碑
   - 阶段性评估安排
   - 计划调整机制

5. **学习内容安排**
   - 新知识学习计划
   - 复习巩固计划
   - 练习训练计划
   - 拓展提高计划

6. **学习方法建议**
   - 高效学习技巧
   - 记忆方法运用
   - 理解策略指导
   - 应用练习方法

7. **计划执行保障**
   - 学习环境优化
   - 学习工具准备
   - 监督检查机制
   - 激励奖惩措施

8. **应急调整预案**
   - 时间冲突的处理
   - 学习进度的调整
   - 突发情况的应对
   - 计划优化的方法

请确保计划科学合理、切实可行、富有弹性。""",
            variables=["student_name", "grade", "subjects", "daily_study_time", "weekend_extra_time", "planning_period", "learning_goals", "current_status", "priority_subjects", "study_habits", "constraints"],
            prompt_type=PromptType.USER,
            category="study_planning",
            tags=["学习计划", "时间管理", "目标规划"]
        )
        
        # 学习方法指导模板
        self.templates["study_method_guidance"] = PromptTemplate(
            name="study_method_guidance",
            description="提供针对性的学习方法指导",
            template="""你是一位学习方法研究专家，请为学生提供学习方法指导：

【学生信息】
姓名：{student_name}
年级：{grade}
科目：{subject}
学习困难：{learning_difficulties}

【当前学习方法】
{current_methods}

【学习效果评估】
{learning_effectiveness}

【学习风格特点】
{learning_style}

【改进需求】
{improvement_needs}

请从以下方面提供学习方法指导：

1. **基础学习方法**
   - 预习方法指导
     * 预习的步骤和要点
     * 预习笔记的记录方法
     * 预习问题的提出技巧
   
   - 听课方法指导
     * 课堂注意力集中技巧
     * 笔记记录的方法
     * 课堂互动的策略
   
   - 复习方法指导
     * 复习计划的制定
     * 复习内容的选择
     * 复习效果的检验

2. **记忆方法训练**
   - 机械记忆技巧
   - 理解记忆方法
   - 联想记忆策略
   - 图像记忆技术
   - 重复记忆规律

3. **理解方法指导**
   - 概念理解策略
   - 原理分析方法
   - 知识关联技巧
   - 实例分析方法
   - 类比理解技术

4. **应用方法培养**
   - 问题解决步骤
   - 解题思路训练
   - 方法迁移技巧
   - 创新思维培养
   - 实践应用指导

5. **学习工具使用**
   - 思维导图制作
   - 概念图绘制
   - 学习软件应用
   - 网络资源利用
   - 学习设备优化

6. **学习习惯养成**
   - 良好学习习惯的培养
   - 不良学习习惯的纠正
   - 学习环境的优化
   - 学习节奏的调整
   - 学习动机的维持

7. **自我调节方法**
   - 学习状态的自我监控
   - 学习策略的自我调整
   - 学习效果的自我评价
   - 学习问题的自我诊断
   - 学习目标的自我管理

8. **实践训练计划**
   - 方法练习的具体安排
   - 技能训练的步骤
   - 效果检验的标准
   - 改进提升的措施

请提供具体可操作的方法指导和训练建议。""",
            variables=["student_name", "grade", "subject", "learning_difficulties", "current_methods", "learning_effectiveness", "learning_style", "improvement_needs"],
            prompt_type=PromptType.USER,
            category="method_guidance",
            tags=["学习方法", "技能训练", "习惯养成"]
        )
        
        # 考试辅导方案模板
        self.templates["exam_preparation_plan"] = PromptTemplate(
            name="exam_preparation_plan",
            description="制定针对性的考试准备和辅导方案",
            template="""你是一位考试辅导专家，请为学生制定考试准备方案：

【考试信息】
考试名称：{exam_name}
考试科目：{exam_subjects}
考试时间：{exam_date}
考试形式：{exam_format}
考试范围：{exam_scope}

【学生信息】
姓名：{student_name}
年级：{grade}
当前水平：{current_level}

【备考时间】
距离考试时间：{preparation_time}
每日可用时间：{daily_time}

【学习状况】
强势科目：{strong_subjects}
薄弱科目：{weak_subjects}
重点关注：{focus_areas}

【历史表现】
{past_performance}

请制定包含以下内容的考试准备方案：

1. **备考目标设定**
   - 总体目标和期望成绩
   - 各科目具体目标
   - 阶段性目标分解
   - 可达成性评估

2. **备考时间规划**
   - 总体时间分配策略
   - 各科目时间分配
   - 每日学习安排
   - 冲刺阶段安排

3. **知识梳理计划**
   - 知识点全面梳理
   - 重点难点突破
   - 薄弱环节补强
   - 知识体系构建

4. **专项训练安排**
   - 题型专项训练
   - 解题技巧训练
   - 速度提升训练
   - 应试技能训练

5. **模拟考试计划**
   - 模拟考试安排
   - 真题练习计划
   - 时间管理训练
   - 心理适应训练

6. **复习策略指导**
   - 第一轮复习：全面梳理
   - 第二轮复习：重点突破
   - 第三轮复习：查漏补缺
   - 冲刺复习：强化提升

7. **应试技巧培训**
   - 答题策略指导
   - 时间分配技巧
   - 心理调节方法
   - 临场应变能力

8. **风险防控措施**
   - 学习进度监控
   - 问题及时发现
   - 调整优化机制
   - 应急预案制定

9. **心理辅导支持**
   - 考试焦虑缓解
   - 自信心建立
   - 压力管理技巧
   - 动机维持方法

请确保方案科学有效、针对性强、可操作性好。""",
            variables=["exam_name", "exam_subjects", "exam_date", "exam_format", "exam_scope", "student_name", "grade", "current_level", "preparation_time", "daily_time", "strong_subjects", "weak_subjects", "focus_areas", "past_performance"],
            prompt_type=PromptType.USER,
            category="exam_preparation",
            tags=["考试辅导", "备考计划", "应试技巧"]
        )
        
        # 学习资源推荐模板
        self.templates["learning_resource_recommendation"] = PromptTemplate(
            name="learning_resource_recommendation",
            description="推荐适合的学习资源和材料",
            template="""你是一位学习资源专家，请为学生推荐合适的学习资源：

【学生信息】
姓名：{student_name}
年级：{grade}
科目：{subject}
学习水平：{learning_level}

【学习需求】
{learning_needs}

【学习目标】
{learning_objectives}

【学习偏好】
{learning_preferences}

【资源类型需求】
{resource_types}

【使用环境】
设备条件：{device_conditions}
网络条件：{network_conditions}
时间安排：{time_arrangement}

请从以下类别推荐学习资源：

1. **教材和参考书**
   - 主教材推荐及使用建议
   - 辅助教材和参考书
   - 练习册和习题集
   - 工具书和字典

2. **数字化学习资源**
   - 在线课程平台推荐
   - 学习APP和软件
   - 教学视频资源
   - 互动学习工具

3. **多媒体资源**
   - 教学视频和动画
   - 音频学习材料
   - 图像和图表资源
   - 虚拟实验和仿真

4. **实践学习资源**
   - 实验器材和工具
   - 实践活动指南
   - 项目学习资源
   - 社会实践机会

5. **评估和测试资源**
   - 在线测试平台
   - 模拟考试系统
   - 自我评估工具
   - 学习进度跟踪

6. **社交学习资源**
   - 学习社区和论坛
   - 同伴学习平台
   - 师生互动工具
   - 家长参与资源

7. **个性化学习工具**
   - 自适应学习系统
   - 个性化推荐引擎
   - 学习分析工具
   - 智能辅导系统

8. **资源使用指导**
   - 资源选择标准
   - 使用方法建议
   - 效果评估方法
   - 资源整合策略

9. **免费和付费资源**
   - 优质免费资源推荐
   - 性价比高的付费资源
   - 资源获取渠道
   - 使用注意事项

请提供具体的资源名称、获取方式和使用建议。""",
            variables=["student_name", "grade", "subject", "learning_level", "learning_needs", "learning_objectives", "learning_preferences", "resource_types", "device_conditions", "network_conditions", "time_arrangement"],
            prompt_type=PromptType.USER,
            category="resource_recommendation",
            tags=["学习资源", "工具推荐", "材料选择"]
        )
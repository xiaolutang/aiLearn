# -*- coding: utf-8 -*-
"""
课堂AI助手相关提示词模板
包含实时学情分析、互动内容生成、教学建议等功能
"""

from .base_prompts import BasePromptTemplate, PromptTemplate, PromptType

class ClassroomPrompts(BasePromptTemplate):
    """课堂AI助手提示词模板类"""
    
    def _load_templates(self):
        """加载课堂AI助手相关的提示词模板"""
        
        # 实时学情分析模板
        self.templates["real_time_analysis"] = PromptTemplate(
            name="real_time_analysis",
            description="实时分析课堂学习情况和学生状态",
            template="""你是一位智能课堂分析师，请对当前课堂情况进行实时分析：

【课堂基本信息】
科目：{subject}
年级：{grade}
班级：{class_name}
课题：{lesson_topic}
课堂时间：{class_time}
学生人数：{student_count}

【当前教学环节】
教学阶段：{teaching_stage}
教学内容：{teaching_content}
教学方法：{teaching_method}
已用时间：{elapsed_time}分钟

【学生参与数据】
{student_participation_data}

【学习行为观察】
{learning_behavior_data}

【互动反馈数据】
{interaction_feedback_data}

【技术监测数据】
{technology_monitoring_data}

请进行以下实时分析：

1. **整体学习状态评估**
   - 班级整体注意力水平
   - 学习参与度评估
   - 理解程度初步判断
   - 学习氛围和情绪状态

2. **个体学习状态识别**
   - 积极参与的学生
   - 需要关注的学生
   - 可能遇到困难的学生
   - 学习状态异常的学生

3. **教学效果实时评估**
   - 教学内容的接受程度
   - 教学方法的适用性
   - 教学节奏的合理性
   - 师生互动的有效性

4. **学习困难预警**
   - 理解困难的征象
   - 注意力分散的表现
   - 学习疲劳的迹象
   - 情绪波动的观察

5. **课堂动态趋势**
   - 参与度变化趋势
   - 理解程度发展趋势
   - 注意力变化规律
   - 互动质量变化

6. **即时调整建议**
   - 教学策略调整建议
   - 互动方式优化建议
   - 节奏控制建议
   - 关注重点建议

7. **预测和预警**
   - 后续学习效果预测
   - 可能出现的问题预警
   - 需要重点关注的环节
   - 建议的应对措施

请提供及时、准确、可操作的分析结果。""",
            variables=["subject", "grade", "class_name", "lesson_topic", "class_time", "student_count", "teaching_stage", "teaching_content", "teaching_method", "elapsed_time", "student_participation_data", "learning_behavior_data", "interaction_feedback_data", "technology_monitoring_data"],
            prompt_type=PromptType.USER,
            category="real_time_analysis",
            tags=["实时分析", "课堂监测", "学情评估"]
        )
        
        # 互动内容生成模板
        self.templates["interactive_content_generation"] = PromptTemplate(
            name="interactive_content_generation",
            description="生成课堂互动内容和活动",
            template="""你是一位课堂互动设计专家，请为当前课堂生成互动内容：

【课堂信息】
科目：{subject}
年级：{grade}
课题：{lesson_topic}
教学目标：{teaching_objectives}

【当前教学状况】
教学进度：{teaching_progress}
学生状态：{student_status}
课堂氛围：{classroom_atmosphere}
时间安排：{time_allocation}

【互动需求】
互动目的：{interaction_purpose}
互动类型：{interaction_type}
参与方式：{participation_method}
时间限制：{time_limit}

【学生特点】
学习水平：{learning_level}
参与偏好：{participation_preferences}
注意力状况：{attention_status}

请设计以下类型的互动内容：

1. **知识检测互动**
   - 快速问答设计
     * 问题设计（3-5个）
     * 答案选项设置
     * 难度梯度安排
     * 时间分配建议
   
   - 概念辨析活动
     * 概念对比题目
     * 判断正误题目
     * 概念应用题目

2. **思维启发互动**
   - 开放性问题设计
     * 发散思维问题
     * 批判思维问题
     * 创新思维问题
   
   - 情境分析活动
     * 案例分析题目
     * 问题解决情境
     * 实际应用场景

3. **协作学习互动**
   - 小组讨论设计
     * 讨论主题设定
     * 角色分工安排
     * 成果展示方式
   
   - 同伴互助活动
     * 互相提问环节
     * 知识分享活动
     * 错误纠正练习

4. **游戏化学习互动**
   - 竞赛类活动
     * 知识竞赛设计
     * 团队对抗赛
     * 个人挑战赛
   
   - 角色扮演活动
     * 角色设定
     * 情境模拟
     * 表演展示

5. **技术增强互动**
   - 数字化工具应用
     * 在线投票活动
     * 实时反馈收集
     * 多媒体展示
   
   - 虚拟实验互动
     * 模拟操作活动
     * 数据分析练习
     * 结果预测游戏

6. **评估反馈互动**
   - 自我评估活动
     * 学习效果自评
     * 理解程度检测
     * 困难点识别
   
   - 同伴评估活动
     * 互相评价练习
     * 作品点评活动
     * 改进建议交流

7. **实施指导**
   - 活动组织步骤
   - 教师引导要点
   - 学生参与指导
   - 效果评估方法

请确保互动内容有趣、有效、易于实施。""",
            variables=["subject", "grade", "lesson_topic", "teaching_objectives", "teaching_progress", "student_status", "classroom_atmosphere", "time_allocation", "interaction_purpose", "interaction_type", "participation_method", "time_limit", "learning_level", "participation_preferences", "attention_status"],
            prompt_type=PromptType.USER,
            category="interactive_content",
            tags=["互动设计", "课堂活动", "参与式学习"]
        )
        
        # 教学建议生成模板
        self.templates["teaching_suggestions"] = PromptTemplate(
            name="teaching_suggestions",
            description="基于课堂情况提供教学改进建议",
            template="""你是一位教学指导专家，请基于当前课堂情况提供教学建议：

【课堂基本信息】
科目：{subject}
年级：{grade}
课题：{lesson_topic}
教学目标：{teaching_objectives}
课堂类型：{class_type}

【当前教学情况】
教学方法：{current_teaching_method}
教学进度：{teaching_progress}
教学效果：{teaching_effectiveness}
学生反应：{student_response}

【观察到的问题】
{observed_issues}

【学生学习数据】
{student_learning_data}

【课堂环境因素】
{classroom_environment}

【教师需求】
{teacher_needs}

请从以下方面提供教学建议：

1. **教学策略优化**
   - 当前策略的优缺点分析
   - 策略调整的具体建议
   - 替代策略的推荐
   - 策略组合的建议

2. **教学方法改进**
   - 讲授方法的优化
   - 互动方法的增强
   - 实践方法的改进
   - 评估方法的完善

3. **课堂管理建议**
   - 注意力管理策略
   - 纪律维护方法
   - 参与度提升技巧
   - 时间管理优化

4. **个性化教学指导**
   - 差异化教学建议
   - 分层教学策略
   - 个别辅导方案
   - 特殊需求关注

5. **技术工具应用**
   - 教学技术的有效运用
   - 数字化工具的选择
   - 多媒体资源的整合
   - 在线平台的利用

6. **评估和反馈改进**
   - 形成性评估的设计
   - 即时反馈的提供
   - 学习效果的监测
   - 调整机制的建立

7. **课堂氛围营造**
   - 积极氛围的创建
   - 学习动机的激发
   - 师生关系的改善
   - 同伴合作的促进

8. **后续教学规划**
   - 下节课的准备建议
   - 单元教学的调整
   - 长期目标的规划
   - 持续改进的方向

9. **专业发展建议**
   - 教学技能的提升
   - 专业知识的更新
   - 教学研究的参与
   - 同行交流的加强

请提供具体、实用、可操作的教学改进建议。""",
            variables=["subject", "grade", "lesson_topic", "teaching_objectives", "class_type", "current_teaching_method", "teaching_progress", "teaching_effectiveness", "student_response", "observed_issues", "student_learning_data", "classroom_environment", "teacher_needs"],
            prompt_type=PromptType.USER,
            category="teaching_suggestions",
            tags=["教学建议", "策略优化", "方法改进"]
        )
        
        # 课堂问题诊断模板
        self.templates["classroom_problem_diagnosis"] = PromptTemplate(
            name="classroom_problem_diagnosis",
            description="诊断课堂教学中的问题和挑战",
            template="""你是一位课堂诊断专家，请对当前课堂问题进行深入分析：

【课堂基本信息】
科目：{subject}
年级：{grade}
班级规模：{class_size}
课题：{lesson_topic}

【问题现象描述】
{problem_description}

【观察数据】
学生参与度：{participation_rate}
理解程度：{comprehension_level}
注意力状况：{attention_status}
互动质量：{interaction_quality}

【教学过程记录】
{teaching_process_record}

【学生反馈信息】
{student_feedback}

【环境因素】
{environmental_factors}

请进行以下问题诊断：

1. **问题识别和分类**
   - 教学内容相关问题
     * 内容难度不当
     * 内容组织混乱
     * 重点不够突出
     * 逻辑关系不清
   
   - 教学方法相关问题
     * 方法选择不当
     * 方法运用不熟练
     * 缺乏方法变化
     * 互动设计不足
   
   - 学生状态相关问题
     * 基础知识不足
     * 学习动机缺乏
     * 注意力不集中
     * 参与积极性低

2. **问题原因分析**
   - 直接原因识别
   - 根本原因挖掘
   - 系统性因素分析
   - 偶然性因素识别

3. **问题影响评估**
   - 对学习效果的影响
   - 对课堂氛围的影响
   - 对师生关系的影响
   - 对后续教学的影响

4. **问题严重程度判断**
   - 紧急程度评估
   - 重要程度评估
   - 影响范围评估
   - 解决难度评估

5. **问题解决优先级**
   - 立即解决的问题
   - 短期解决的问题
   - 中期解决的问题
   - 长期关注的问题

6. **解决方案建议**
   - 即时应对措施
   - 短期改进方案
   - 长期优化策略
   - 预防措施建议

7. **实施指导**
   - 解决步骤安排
   - 资源需求分析
   - 风险评估和控制
   - 效果监测方法

8. **预防策略**
   - 类似问题的预防
   - 早期预警机制
   - 持续改进机制
   - 能力建设建议

请提供准确的问题诊断和有效的解决方案。""",
            variables=["subject", "grade", "class_size", "lesson_topic", "problem_description", "participation_rate", "comprehension_level", "attention_status", "interaction_quality", "teaching_process_record", "student_feedback", "environmental_factors"],
            prompt_type=PromptType.USER,
            category="problem_diagnosis",
            tags=["问题诊断", "课堂分析", "解决方案"]
        )
        
        # 学习效果评估模板
        self.templates["learning_effectiveness_assessment"] = PromptTemplate(
            name="learning_effectiveness_assessment",
            description="评估课堂学习效果和教学质量",
            template="""你是一位学习效果评估专家，请对本节课的学习效果进行综合评估：

【课堂基本信息】
科目：{subject}
年级：{grade}
课题：{lesson_topic}
教学目标：{teaching_objectives}
课堂时长：{class_duration}分钟

【教学过程数据】
{teaching_process_data}

【学生表现数据】
{student_performance_data}

【互动参与数据】
{interaction_data}

【评估测试结果】
{assessment_results}

【课后反馈】
{post_class_feedback}

请从以下维度进行学习效果评估：

1. **目标达成度评估**
   - 知识目标达成情况
     * 核心概念掌握程度
     * 知识点理解深度
     * 知识结构建构情况
   
   - 能力目标达成情况
     * 思维能力发展
     * 实践能力提升
     * 问题解决能力
   
   - 情感目标达成情况
     * 学习兴趣激发
     * 学习态度改善
     * 价值观培养

2. **学习过程质量评估**
   - 学习参与度
     * 主动参与程度
     * 互动质量水平
     * 合作学习效果
   
   - 学习深度
     * 思维参与程度
     * 理解层次深度
     * 应用迁移能力
   
   - 学习效率
     * 时间利用效率
     * 学习节奏适宜性
     * 注意力集中度

3. **个体差异分析**
   - 优秀学生表现
     * 突出表现识别
     * 潜能发挥程度
     * 引领作用发挥
   
   - 中等学生表现
     * 基本目标达成
     * 进步空间识别
     * 支持需求分析
   
   - 困难学生表现
     * 困难点识别
     * 支持效果评估
     * 改进需求分析

4. **教学效果评估**
   - 教学方法有效性
   - 教学内容适宜性
   - 教学节奏合理性
   - 师生互动质量

5. **学习成果质量**
   - 知识掌握的准确性
   - 理解的深度和广度
   - 应用能力的表现
   - 创新思维的体现

6. **持续性学习评估**
   - 学习兴趣的持续性
   - 学习动机的稳定性
   - 自主学习能力
   - 后续学习准备度

7. **改进建议**
   - 教学策略调整
   - 学习支持优化
   - 评估方式改进
   - 后续教学规划

8. **综合评价**
   - 整体效果评分（1-10分）
   - 主要成功因素
   - 主要改进空间
   - 经验总结提炼

请提供客观、全面、具有指导意义的评估报告。""",
            variables=["subject", "grade", "lesson_topic", "teaching_objectives", "class_duration", "teaching_process_data", "student_performance_data", "interaction_data", "assessment_results", "post_class_feedback"],
            prompt_type=PromptType.USER,
            category="effectiveness_assessment",
            tags=["效果评估", "质量分析", "教学反思"]
        )
        
        # 课堂氛围分析模板
        self.templates["classroom_atmosphere_analysis"] = PromptTemplate(
            name="classroom_atmosphere_analysis",
            description="分析和评估课堂学习氛围",
            template="""你是一位课堂氛围分析专家，请对当前课堂氛围进行深入分析：

【课堂基本信息】
科目：{subject}
年级：{grade}
班级：{class_name}
课题：{lesson_topic}
时间：{class_time}

【氛围观察数据】
{atmosphere_observation}

【学生行为表现】
{student_behavior}

【师生互动情况】
{teacher_student_interaction}

【课堂环境因素】
{classroom_environment}

【情绪状态监测】
{emotional_state_monitoring}

请从以下维度分析课堂氛围：

1. **整体氛围特征**
   - 氛围类型识别
     * 活跃型：热烈讨论、积极参与
     * 专注型：安静思考、认真听讲
     * 轻松型：愉快学习、自然互动
     * 紧张型：压抑沉闷、缺乏活力
   
   - 氛围强度评估
     * 高强度：情绪饱满、参与热烈
     * 中强度：状态良好、参与适中
     * 低强度：状态一般、参与较少

2. **情感氛围分析**
   - 积极情感表现
     * 学习兴趣和热情
     * 成就感和自信心
     * 好奇心和探索欲
     * 合作精神和友善
   
   - 消极情感识别
     * 焦虑和紧张情绪
     * 厌倦和无聊状态
     * 挫败感和失望
     * 冲突和对立情绪

3. **学习氛围评估**
   - 学术氛围
     * 求知欲的表现
     * 思辨精神的体现
     * 学术讨论的质量
     * 知识分享的意愿
   
   - 合作氛围
     * 团队协作精神
     * 互助学习行为
     * 包容和理解态度
     * 共同进步意识

4. **师生关系氛围**
   - 信任关系
     * 学生对教师的信任
     * 教师对学生的信任
     * 相互尊重程度
   
   - 沟通质量
     * 沟通的开放性
     * 表达的自由度
     * 反馈的及时性
     * 理解的准确性

5. **同伴关系氛围**
   - 同伴支持
     * 互相帮助行为
     * 鼓励和支持表现
     * 知识分享意愿
   
   - 竞争与合作
     * 良性竞争氛围
     * 合作学习效果
     * 团队凝聚力

6. **氛围影响因素**
   - 教师因素
     * 教学风格影响
     * 情绪状态传递
     * 管理方式效果
   
   - 学生因素
     * 个性特征影响
     * 学习状态影响
     * 群体动力作用
   
   - 环境因素
     * 物理环境影响
     * 时间安排影响
     * 外部干扰因素

7. **氛围优化建议**
   - 积极氛围的维持
   - 消极氛围的改善
   - 氛围调节策略
   - 长期氛围建设

8. **氛围监测建议**
   - 氛围指标设定
   - 监测方法选择
   - 预警机制建立
   - 改进措施制定

请提供详细的氛围分析和具体的优化建议。""",
            variables=["subject", "grade", "class_name", "lesson_topic", "class_time", "atmosphere_observation", "student_behavior", "teacher_student_interaction", "classroom_environment", "emotional_state_monitoring"],
            prompt_type=PromptType.USER,
            category="atmosphere_analysis",
            tags=["课堂氛围", "情感分析", "环境评估"]
        )
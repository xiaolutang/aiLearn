# -*- coding: utf-8 -*-
"""
学情分析相关提示词模板
包含成绩分析、学习状态评估、薄弱环节识别等功能
"""

from .base_prompts import BasePromptTemplate, PromptTemplate, PromptType

class LearningPrompts(BasePromptTemplate):
    """学情分析提示词模板类"""
    
    def _load_templates(self):
        """加载学情分析相关的提示词模板"""
        
        # 综合学情分析模板
        self.templates["comprehensive_analysis"] = PromptTemplate(
            name="comprehensive_analysis",
            description="对学生的综合学习情况进行全面分析",
            template="""你是一位专业的学情分析师，请对以下学生的学习情况进行综合分析：

【学生基本信息】
姓名：{student_name}
年级：{grade}
班级：{class_name}
分析时间段：{time_period}

【成绩数据】
{score_data}

【学习行为数据】
{behavior_data}

【作业完成情况】
{homework_data}

请从以下维度进行综合分析：

1. **学习成绩分析**
   - 各科目成绩水平及排名
   - 成绩变化趋势和波动情况
   - 强势科目和薄弱科目识别
   - 与班级平均水平的对比

2. **学习能力评估**
   - 理解能力：概念掌握和知识理解程度
   - 应用能力：知识运用和问题解决能力
   - 分析能力：逻辑思维和批判性思维
   - 创新能力：创造性思维和独立思考

3. **学习习惯分析**
   - 学习态度和学习动机
   - 学习方法和学习策略
   - 时间管理和学习效率
   - 自主学习和合作学习能力

4. **学习状态评估**
   - 学习兴趣和参与度
   - 学习压力和心理状态
   - 注意力集中程度
   - 学习持续性和稳定性

5. **发展潜力分析**
   - 学习潜能和发展空间
   - 特长和优势领域
   - 可能的发展方向
   - 需要重点关注的方面

6. **问题诊断**
   - 主要学习问题识别
   - 问题产生的可能原因
   - 问题的严重程度评估
   - 解决问题的紧迫性

请提供详细的分析报告和具体的改进建议。""",
            variables=["student_name", "grade", "class_name", "time_period", "score_data", "behavior_data", "homework_data"],
            prompt_type=PromptType.USER,
            category="learning_analysis",
            tags=["综合分析", "学情评估", "能力分析"]
        )
        
        # 薄弱环节分析模板
        self.templates["weakness_analysis"] = PromptTemplate(
            name="weakness_analysis",
            description="深入分析学生的薄弱环节和学习困难",
            template="""你是一位学习诊断专家，请深入分析学生的薄弱环节：

【学生信息】
姓名：{student_name}
科目：{subject}
年级：{grade}

【错题数据】
{error_data}

【知识点掌握情况】
{knowledge_mastery}

【学习过程数据】
{learning_process}

请进行以下薄弱环节分析：

1. **知识薄弱点识别**
   - 掌握不牢固的知识点
   - 理解有偏差的概念
   - 遗忘严重的内容
   - 混淆易错的知识点

2. **能力薄弱点分析**
   - 基础技能缺陷
   - 思维方法不当
   - 解题策略缺失
   - 表达能力不足

3. **学习方法问题**
   - 学习策略不当
   - 记忆方法低效
   - 练习方式单一
   - 复习计划缺失

4. **认知障碍分析**
   - 先入为主的错误观念
   - 思维定势的负面影响
   - 认知负荷过重
   - 元认知能力不足

5. **情感因素影响**
   - 学习焦虑和恐惧
   - 自信心不足
   - 学习动机缺乏
   - 挫折承受能力弱

6. **外部因素分析**
   - 教学方式不适应
   - 学习环境影响
   - 同伴关系影响
   - 家庭支持不足

7. **改进策略建议**
   - 针对性的补强方案
   - 学习方法调整建议
   - 心理调适策略
   - 环境优化建议

请提供具体的诊断结果和可操作的改进方案。""",
            variables=["student_name", "subject", "grade", "error_data", "knowledge_mastery", "learning_process"],
            prompt_type=PromptType.USER,
            category="weakness_analysis",
            tags=["薄弱环节", "学习诊断", "问题分析"]
        )
        
        # 学习进度跟踪模板
        self.templates["progress_tracking"] = PromptTemplate(
            name="progress_tracking",
            description="跟踪和分析学生的学习进度变化",
            template="""你是一位学习进度分析专家，请分析学生的学习进度情况：

【学生信息】
姓名：{student_name}
科目：{subject}
跟踪周期：{tracking_period}

【历史成绩数据】
{historical_scores}

【学习目标】
{learning_goals}

【当前进度】
{current_progress}

【学习活动记录】
{learning_activities}

请进行以下进度分析：

1. **进度完成情况**
   - 整体进度完成率
   - 各阶段目标达成情况
   - 超前或滞后的具体表现
   - 进度偏差的程度分析

2. **学习速度分析**
   - 知识掌握速度
   - 技能形成速度
   - 不同内容的学习效率
   - 学习速度的变化趋势

3. **质量与效果评估**
   - 学习质量的变化
   - 掌握程度的深浅
   - 应用能力的发展
   - 迁移能力的表现

4. **学习曲线分析**
   - 学习曲线的形态特征
   - 学习高峰和低谷期
   - 平台期的识别和分析
   - 突破性进步的时机

5. **影响因素识别**
   - 促进进步的积极因素
   - 阻碍进步的消极因素
   - 外部环境的影响
   - 内在动机的变化

6. **预测与规划**
   - 后续学习进度预测
   - 可能遇到的挑战
   - 需要调整的策略
   - 阶段性目标的设定

7. **改进建议**
   - 进度调整的具体措施
   - 学习策略的优化
   - 时间安排的改进
   - 支持资源的配置

请提供详细的进度分析报告和后续规划建议。""",
            variables=["student_name", "subject", "tracking_period", "historical_scores", "learning_goals", "current_progress", "learning_activities"],
            prompt_type=PromptType.USER,
            category="progress_tracking",
            tags=["进度跟踪", "学习曲线", "预测分析"]
        )
        
        # 班级学情对比分析模板
        self.templates["class_comparison"] = PromptTemplate(
            name="class_comparison",
            description="分析学生在班级中的相对表现和位置",
            template="""你是一位班级学情分析专家，请分析学生在班级中的表现：

【班级信息】
班级：{class_name}
年级：{grade}
学生总数：{total_students}
分析科目：{subject}

【目标学生信息】
姓名：{student_name}
学号：{student_id}

【班级成绩分布】
{class_score_distribution}

【学生成绩数据】
{student_scores}

【班级平均数据】
{class_average_data}

请进行以下对比分析：

1. **成绩位置分析**
   - 在班级中的排名情况
   - 与班级平均分的差距
   - 在各分数段的分布位置
   - 相对优势和劣势科目

2. **发展趋势对比**
   - 个人进步幅度与班级对比
   - 成绩稳定性与班级对比
   - 学习速度与同伴对比
   - 潜力发挥程度分析

3. **能力水平对比**
   - 各项能力在班级中的水平
   - 特长领域的突出程度
   - 薄弱环节的普遍性
   - 综合素质的相对位置

4. **学习特点分析**
   - 学习风格的独特性
   - 学习习惯的优劣势
   - 参与度和积极性表现
   - 合作学习的适应性

5. **同伴关系影响**
   - 学习伙伴的选择
   - 同伴学习的效果
   - 竞争与合作的平衡
   - 班级氛围的适应度

6. **发展空间评估**
   - 在班级中的提升空间
   - 可以学习的榜样
   - 可以帮助的同学
   - 班级资源的利用

7. **个性化建议**
   - 基于班级情况的学习策略
   - 同伴学习的组织建议
   - 差异化发展的方向
   - 班级活动的参与建议

请提供详细的对比分析和个性化发展建议。""",
            variables=["class_name", "grade", "total_students", "subject", "student_name", "student_id", "class_score_distribution", "student_scores", "class_average_data"],
            prompt_type=PromptType.USER,
            category="class_comparison",
            tags=["班级对比", "相对分析", "同伴学习"]
        )
        
        # 学习风格分析模板
        self.templates["learning_style_analysis"] = PromptTemplate(
            name="learning_style_analysis",
            description="分析学生的学习风格和偏好特征",
            template="""你是一位学习风格研究专家，请分析学生的学习风格特征：

【学生信息】
姓名：{student_name}
年级：{grade}
性别：{gender}

【学习行为观察】
{learning_behavior}

【学习偏好调查】
{learning_preferences}

【学习效果数据】
{learning_effectiveness}

【课堂表现记录】
{classroom_performance}

请从以下维度分析学习风格：

1. **信息接收偏好**
   - 视觉型：通过图像、图表、颜色学习
   - 听觉型：通过声音、音乐、讨论学习
   - 动觉型：通过动手、体验、实践学习
   - 读写型：通过文字、笔记、阅读学习

2. **信息处理方式**
   - 序列型：喜欢按步骤、有逻辑地学习
   - 随机型：喜欢跳跃式、关联性学习
   - 整体型：先看全貌再关注细节
   - 细节型：先掌握细节再构建整体

3. **思维特征分析**
   - 分析型思维：逻辑推理、系统分析
   - 综合型思维：整体把握、直觉判断
   - 抽象型思维：概念理解、理论思考
   - 具体型思维：实例理解、实际应用

4. **学习环境偏好**
   - 安静环境 vs 有背景音的环境
   - 独立学习 vs 小组合作学习
   - 结构化环境 vs 灵活自由环境
   - 竞争环境 vs 合作环境

5. **学习节奏特点**
   - 学习时间偏好（早晨/下午/晚上）
   - 注意力持续时间
   - 休息频率需求
   - 学习强度承受能力

6. **动机和态度**
   - 内在动机 vs 外在动机
   - 成就导向 vs 过程导向
   - 风险承受能力
   - 挫折应对方式

7. **个性化学习建议**
   - 适合的学习方法
   - 推荐的学习工具
   - 环境优化建议
   - 学习策略调整

请提供详细的学习风格分析和个性化学习建议。""",
            variables=["student_name", "grade", "gender", "learning_behavior", "learning_preferences", "learning_effectiveness", "classroom_performance"],
            prompt_type=PromptType.USER,
            category="learning_style",
            tags=["学习风格", "个性化", "学习偏好"]
        )
        
        # 学习动机分析模板
        self.templates["motivation_analysis"] = PromptTemplate(
            name="motivation_analysis",
            description="分析学生的学习动机和激励因素",
            template="""你是一位学习动机研究专家，请分析学生的学习动机状况：

【学生信息】
姓名：{student_name}
年级：{grade}
科目关注：{subject_focus}

【学习表现数据】
{performance_data}

【行为观察记录】
{behavior_observation}

【访谈或问卷结果】
{survey_results}

【家庭背景信息】
{family_background}

请从以下角度分析学习动机：

1. **动机类型识别**
   - 内在动机：兴趣、好奇心、成就感
   - 外在动机：奖励、认可、避免惩罚
   - 整合动机：价值认同、目标一致
   - 无动机状态：缺乏动力、消极应对

2. **动机强度评估**
   - 学习投入程度
   - 持续努力的意愿
   - 面对困难的坚持性
   - 主动学习的频率

3. **动机来源分析**
   - 个人兴趣和爱好
   - 成就需要和竞争意识
   - 社会期望和压力
   - 未来目标和理想

4. **影响因素识别**
   - 积极影响因素
     * 成功体验和成就感
     * 教师的鼓励和支持
     * 同伴的认可和友谊
     * 家庭的理解和支持
   
   - 消极影响因素
     * 失败经历和挫折感
     * 过度的压力和期望
     * 单调的学习内容
     * 不当的评价方式

5. **动机发展趋势**
   - 动机水平的变化轨迹
   - 不同阶段的动机特点
   - 关键转折点的识别
   - 未来发展的预测

6. **动机障碍诊断**
   - 学习倦怠的表现
   - 习得性无助的迹象
   - 完美主义的负面影响
   - 焦虑和恐惧的干扰

7. **激励策略建议**
   - 内在动机的培养方法
   - 外在激励的合理运用
   - 目标设定的指导
   - 环境优化的措施

请提供详细的动机分析和具体的激励建议。""",
            variables=["student_name", "grade", "subject_focus", "performance_data", "behavior_observation", "survey_results", "family_background"],
            prompt_type=PromptType.USER,
            category="motivation_analysis",
            tags=["学习动机", "激励策略", "心理分析"]
        )
# -*- coding: utf-8 -*-
"""
教材分析相关提示词模板
包含内容分析、知识点提取、难度评估等功能
"""

from .base_prompts import BasePromptTemplate, PromptTemplate, PromptType

class TeachingPrompts(BasePromptTemplate):
    """教材分析提示词模板类"""
    
    def _load_templates(self):
        """加载教材分析相关的提示词模板"""
        
        # 教材内容分析模板
        self.templates["content_analysis"] = PromptTemplate(
            name="content_analysis",
            description="分析教材内容的结构、主题和教学目标",
            template="""你是一位资深的教育专家和教材分析师。请对以下教材内容进行深入分析：

【教材信息】
科目：{subject}
年级：{grade}
章节：{chapter}

【教材内容】
{content}

请从以下几个维度进行分析：

1. **内容结构分析**
   - 章节的逻辑结构和组织方式
   - 内容的层次关系和递进逻辑
   - 重点内容和辅助内容的分布

2. **教学目标识别**
   - 知识目标：学生需要掌握的核心概念和事实
   - 能力目标：需要培养的技能和思维能力
   - 情感目标：价值观和态度的培养

3. **内容特点分析**
   - 内容的抽象程度和复杂性
   - 与前后章节的关联性
   - 实际应用价值和生活联系

4. **教学建议**
   - 推荐的教学方法和策略
   - 可能的教学难点和解决方案
   - 适合的教学活动和练习形式

请以结构化的方式输出分析结果，确保内容准确、全面且具有实用性。""",
            variables=["subject", "grade", "chapter", "content"],
            prompt_type=PromptType.USER,
            category="teaching_analysis",
            tags=["内容分析", "教学目标", "教学建议"]
        )
        
        # 知识点提取模板
        self.templates["knowledge_extraction"] = PromptTemplate(
            name="knowledge_extraction",
            description="从教材内容中提取和整理知识点",
            template="""你是一位专业的知识工程师，擅长从教材中提取和组织知识点。请对以下教材内容进行知识点提取：

【教材信息】
科目：{subject}
年级：{grade}
章节：{chapter}

【教材内容】
{content}

请按照以下要求提取知识点：

1. **核心概念**
   - 识别本章节的核心概念和定义
   - 标注概念的重要程度（核心/重要/一般）
   - 说明概念之间的关系

2. **知识点分类**
   - 事实性知识：需要记忆的具体事实、数据、术语
   - 概念性知识：概念、原理、理论的理解
   - 程序性知识：操作步骤、方法、技能
   - 元认知知识：学习策略、思维方法

3. **知识点层次**
   - 一级知识点：章节主要内容
   - 二级知识点：具体的概念和原理
   - 三级知识点：细节和例子

4. **知识点关联**
   - 与前置知识的关系
   - 与后续学习的关系
   - 跨学科的关联

5. **掌握要求**
   - 了解：基本认识和感知
   - 理解：深入理解和解释
   - 应用：实际运用和解决问题
   - 分析：分解和分析复杂问题

请以JSON格式输出结果，包含知识点的详细信息和层次结构。""",
            variables=["subject", "grade", "chapter", "content"],
            prompt_type=PromptType.USER,
            category="knowledge_extraction",
            tags=["知识点", "概念提取", "知识结构"]
        )
        
        # 难度分析模板
        self.templates["difficulty_analysis"] = PromptTemplate(
            name="difficulty_analysis",
            description="分析教材内容的学习难度和认知负荷",
            template="""你是一位教育心理学专家，请对以下教材内容进行学习难度分析：

【教材信息】
科目：{subject}
年级：{grade}
学生年龄：{student_age}岁
章节：{chapter}

【教材内容】
{content}

请从以下维度分析学习难度：

1. **认知难度评估**
   - 概念抽象程度（1-5分，5分最抽象）
   - 逻辑复杂性（1-5分，5分最复杂）
   - 记忆负荷（1-5分，5分负荷最大）
   - 理解深度要求（1-5分，5分要求最深）

2. **学习障碍分析**
   - 可能的理解难点
   - 常见的学习误区
   - 认知冲突点
   - 前置知识要求

3. **年龄适应性**
   - 与学生认知发展阶段的匹配度
   - 语言表达的适宜性
   - 例子和情境的贴近性
   - 注意力和兴趣的维持能力

4. **学习时间预估**
   - 理解基本概念所需时间
   - 掌握核心技能所需时间
   - 达到熟练应用所需时间
   - 建议的学习节奏

5. **分层教学建议**
   - 基础层：最低掌握要求
   - 标准层：一般掌握要求
   - 提高层：深入掌握要求
   - 个性化调整策略

请给出具体的难度评分和详细的分析说明。""",
            variables=["subject", "grade", "student_age", "chapter", "content"],
            prompt_type=PromptType.USER,
            category="difficulty_analysis",
            tags=["难度评估", "认知负荷", "学习障碍"]
        )
        
        # 教学设计模板
        self.templates["teaching_design"] = PromptTemplate(
            name="teaching_design",
            description="基于教材内容设计具体的教学方案",
            template="""你是一位优秀的教学设计师，请为以下教材内容设计详细的教学方案：

【教材信息】
科目：{subject}
年级：{grade}
章节：{chapter}
课时：{class_hours}课时
班级规模：{class_size}人

【教材内容】
{content}

【学生特点】
{student_characteristics}

请设计包含以下要素的教学方案：

1. **教学目标设定**
   - 知识与技能目标
   - 过程与方法目标
   - 情感态度价值观目标
   - 可测量的具体指标

2. **教学重难点**
   - 教学重点及突出策略
   - 教学难点及突破方法
   - 关键问题设计

3. **教学流程设计**
   - 导入环节（5-10分钟）
   - 新课讲授（20-25分钟）
   - 练习巩固（10-15分钟）
   - 总结提升（3-5分钟）
   - 具体的时间分配

4. **教学方法选择**
   - 主要教学方法及理由
   - 学生活动设计
   - 师生互动方式
   - 多媒体资源运用

5. **评价方案**
   - 形成性评价设计
   - 总结性评价方案
   - 评价标准和工具
   - 反馈机制

6. **作业布置**
   - 基础练习题
   - 拓展思考题
   - 实践应用题
   - 预习准备

请确保教学设计科学合理、操作性强、符合学生认知规律。""",
            variables=["subject", "grade", "chapter", "class_hours", "class_size", "content", "student_characteristics"],
            prompt_type=PromptType.USER,
            category="teaching_design",
            tags=["教学设计", "教学方案", "课堂活动"]
        )
        
        # 练习题生成模板
        self.templates["exercise_generation"] = PromptTemplate(
            name="exercise_generation",
            description="根据教材内容生成不同类型和难度的练习题",
            template="""你是一位专业的题目设计专家，请根据以下教材内容生成高质量的练习题：

【教材信息】
科目：{subject}
年级：{grade}
章节：{chapter}
知识点：{knowledge_points}

【教材内容】
{content}

【题目要求】
题目数量：{question_count}道
难度分布：{difficulty_distribution}
题型要求：{question_types}

请按照以下要求生成练习题：

1. **题型分布**
   - 选择题：考查基础概念和理解
   - 填空题：考查关键知识点记忆
   - 简答题：考查理解和表达能力
   - 应用题：考查知识运用能力
   - 分析题：考查综合分析能力

2. **难度层次**
   - 基础题（30%）：直接应用概念和公式
   - 中等题（50%）：需要一定的分析和推理
   - 提高题（20%）：综合运用和创新思维

3. **题目质量要求**
   - 题目表述清晰准确
   - 选项设计合理（选择题）
   - 答案唯一且正确
   - 具有一定的区分度
   - 贴近学生生活实际

4. **输出格式**
   - 题目编号和类型
   - 题目内容
   - 标准答案
   - 解题思路
   - 考查知识点
   - 难度等级

请确保题目覆盖主要知识点，难度分布合理，具有良好的教学价值。""",
            variables=["subject", "grade", "chapter", "knowledge_points", "content", "question_count", "difficulty_distribution", "question_types"],
            prompt_type=PromptType.USER,
            category="exercise_generation",
            tags=["练习题", "题目生成", "评估工具"]
        )
        
        # 教材评价模板
        self.templates["textbook_evaluation"] = PromptTemplate(
            name="textbook_evaluation",
            description="对教材质量进行全面评价和改进建议",
            template="""你是一位资深的教材评审专家，请对以下教材内容进行全面评价：

【教材信息】
科目：{subject}
年级：{grade}
出版社：{publisher}
版本：{version}
章节：{chapter}

【教材内容】
{content}

请从以下维度进行评价：

1. **内容质量评价**
   - 科学性：内容的准确性和权威性
   - 系统性：知识结构的完整性和逻辑性
   - 时代性：内容的更新程度和前沿性
   - 适用性：与课程标准的符合程度

2. **教学适用性评价**
   - 年龄适宜性：与学生认知水平的匹配
   - 难度梯度：知识点的递进安排
   - 实用性：理论与实践的结合程度
   - 趣味性：内容的吸引力和参与度

3. **编写质量评价**
   - 语言表达：文字的准确性和可读性
   - 版面设计：布局的合理性和美观性
   - 图表质量：插图和图表的有效性
   - 练习设计：习题的质量和数量

4. **创新特色分析**
   - 教学理念的体现
   - 教学方法的创新
   - 技术手段的运用
   - 文化特色的融入

5. **改进建议**
   - 内容方面的改进点
   - 教学设计的优化建议
   - 版面编排的改进意见
   - 配套资源的完善建议

请给出具体的评分（1-10分）和详细的评价说明。""",
            variables=["subject", "grade", "publisher", "version", "chapter", "content"],
            prompt_type=PromptType.USER,
            category="textbook_evaluation",
            tags=["教材评价", "质量评估", "改进建议"]
        )
        
        # 跨学科关联分析模板
        self.templates["interdisciplinary_analysis"] = PromptTemplate(
            name="interdisciplinary_analysis",
            description="分析教材内容与其他学科的关联性",
            template="""你是一位跨学科教育专家，请分析以下教材内容与其他学科的关联性：

【主要学科】
科目：{subject}
年级：{grade}
章节：{chapter}

【教材内容】
{content}

【关联学科范围】
{related_subjects}

请从以下角度进行跨学科关联分析：

1. **知识关联分析**
   - 概念层面的关联：相同或相似的概念
   - 原理层面的关联：共同的基本原理
   - 方法层面的关联：相似的思维方法
   - 应用层面的关联：共同的应用领域

2. **具体关联点识别**
   - 与数学的关联：计算、逻辑、建模等
   - 与语文的关联：表达、理解、文化等
   - 与科学的关联：实验、观察、推理等
   - 与社会的关联：历史、地理、社会等
   - 与艺术的关联：美学、创造、表现等

3. **跨学科教学机会**
   - 可以整合的教学主题
   - 跨学科项目设计思路
   - 协同教学的可能性
   - 综合实践活动设计

4. **能力培养协同**
   - 共同培养的核心素养
   - 思维能力的协同发展
   - 实践能力的综合提升
   - 创新能力的培养路径

5. **实施建议**
   - 跨学科教学的具体策略
   - 教师协作的组织方式
   - 评价方式的调整建议
   - 资源整合的方法

请提供具体的关联分析和实用的教学建议。""",
            variables=["subject", "grade", "chapter", "content", "related_subjects"],
            prompt_type=PromptType.USER,
            category="interdisciplinary_analysis",
            tags=["跨学科", "关联分析", "整合教学"]
        )
# 🎯 学习计划

## 🧠 学习目标总览

掌握大模型应用开发的核心技能，包括 Prompt 工程、RAG（检索增强生成）、函数调用、模型部署与调优、多模态处理、应用开发与实战项目，最终能够独立设计和开发大模型应用系统。

---

## 📅 学习时间安排

| 阶段 | 时间周期 | 学习主题 | 学习目标 |
|------|----------|----------|----------|
| 第一阶段 | 第1-2周 | Prompt工程、RAG、函数调用 | 掌握Prompt设计、RAG原理与实现、函数调用机制 |
| 第二阶段 | 第3-5周 | 模型理解、调用与部署 | 理解主流大模型（如LLaMA、ChatGLM、Qwen等），掌握模型调用与本地部署 |
| 第三阶段 | 第6-8周 | 应用开发与框架 | 掌握LangChain、LlamaIndex等工具，构建大模型应用 |
| 第四阶段 | 第9-16周 | 项目实战与进阶 | 完成多个实战项目，掌握多模态、微调、性能优化等高级技能 |

---

## 📘 学习内容与每日安排（Markdown格式）

### 📌 第1-2周：Prompt工程、RAG与函数调用（基础核心）

> **目标：掌握大模型应用开发的基础三大核心能力**

#### 第1周：
- **Day 1**：Prompt基础与工程化设计
  - 学习Prompt的结构与设计原则
  - 实践：使用OpenAI API写几个Prompt，测试效果
- **Day 2**：Prompt优化与Chain-of-Thought
  - 学习Few-shot、Zero-shot Prompt
  - 实践：设计一个Chain-of-Thought Prompt解决逻辑问题
- **Day 3**：RAG基础知识
  - 了解RAG的原理、流程与应用场景
  - 学习向量数据库（如FAISS、Pinecone）的基础概念
- **Day 4**：RAG实战入门
  - 使用LangChain + FAISS实现一个简单的RAG系统
- **Day 5**：函数调用（Function Calling）
  - 了解OpenAI函数调用机制
  - 实践：调用API或本地函数处理用户请求
- **Day 6**：Prompt + RAG + 函数调用整合练习
  - 构建一个结合Prompt、RAG与函数调用的简单问答系统
- **Day 7**：复习 + 小项目
  - 综合练习：构建一个基于文档的问答助手

#### 第2周：
- **Day 8**：深入Prompt工程
  - 学习Prompt模板、Prompt优化工具（如PromptFoo）
- **Day 9**：RAG进阶（召回+排序）
  - 学习召回策略、相似度匹配、重排序
- **Day 10**：RAG实战进阶（使用LlamaIndex）
  - 使用LlamaIndex构建更复杂的RAG系统
- **Day 11**：函数调用与工具集成
  - 学习如何集成多个工具（如天气API、数据库查询）
- **Day 12**：构建一个Agent系统
  - 使用LangChain Agent构建一个能自动调用工具的系统
- **Day 13**：综合练习：构建一个文档问答助手（Prompt + RAG + 函数调用）
- **Day 14**：阶段总结与测试
  - 完成一次小测试，评估掌握程度

---

### 📌 第3-5周：模型调用、部署与理解（技术底层）

> **目标：掌握主流大模型的调用方式、部署方式与基本原理**

#### 第3周：
- **Day 15**：了解主流大模型（如LLaMA、ChatGLM、Qwen、Mistral）
- **Day 16**：模型调用方式（OpenAI API、HuggingFace API）
- **Day 17**：本地部署模型（如使用Ollama、LM Studio）
- **Day 18**：本地调用模型（使用Transformers库）
- **Day 19**：模型参数与推理配置（温度、Top-k、Top-p等）
- **Day 20**：模型性能评估（BLEU、ROUGE、人工评估）
- **Day 21**：复习 + 实战练习

#### 第4周：
- **Day 22**：模型量化与压缩（如GGUF、Q4量化）
- **Day 23**：模型部署（Docker、FastAPI、Gradio）
- **Day 24**：模型服务化（部署为API服务）
- **Day 25**：模型安全与伦理（Prompt注入、输出控制）
- **Day 26**：LangChain进阶（Memory、Callbacks、Tools）
- **Day 27**：LlamaIndex进阶（Query Engine、Custom Index）
- **Day 28**：阶段总结与测试

---

### 📌 第6-8周：应用开发与框架整合（工程化）

> **目标：掌握LangChain、LlamaIndex等主流框架，构建完整应用**

#### 第6周：
- **Day 29**：LangChain核心组件（LLM、Prompt、Chain）
- **Day 30**：LangChain Agents与工具链
- **Day 31**：LlamaIndex核心组件（Document、Index、Query）
- **Day 32**：构建一个文档问答系统（LlamaIndex + RAG）
- **Day 33**：构建一个聊天机器人（LangChain + Prompt + RAG）
- **Day 34**：多轮对话与记忆管理（Memory）
- **Day 35**：复习 + 实战练习

#### 第7周：
- **Day 36**：多模态输入处理（图像、音频、视频）
- **Day 37**：多模态模型（如CLIP、BLIP、Qwen-VL）
- **Day 38**：构建一个多模态问答系统
- **Day 39**：构建一个Web应用（Flask/FastAPI + 前端）
- **Day 40**：使用Streamlit构建交互式大模型应用
- **Day 41**：部署一个完整的Web应用（Heroku、Render、Docker）
- **Day 42**：阶段总结与测试

---

### 📌 第9-16周：项目实战与进阶技能（高级应用）

> **目标：完成多个实战项目，掌握高级技能如微调、性能优化等**

#### 第9-10周：
- **Day 43**：选择一个项目方向（如客服助手、文档助手、知识库问答）
- **Day 44**：需求分析与架构设计
- **Day 45**：数据准备与清洗
- **Day 46**：构建核心模块（Prompt、RAG、函数调用）
- **Day 47**：集成LangChain/LlamaIndex模块
- **Day 48**：前端界面开发（可选）
- **Day 49**：部署与测试

#### 第11-12周：
- **Day 50**：学习LoRA微调（低秩适配）
- **Day 51**：使用PEFT库进行LoRA微调
- **Day 52**：微调一个模型用于特定任务（如问答）
- **Day 53**：训练数据准备与标注
- **Day 54**：评估微调效果
- **Day 55**：部署微调后的模型
- **Day 56**：阶段总结与测试

#### 第13-14周：
- **Day 57**：学习推理优化（KV Cache、并行推理）
- **Day 58**：模型压缩与量化部署
- **Day 59**：学习评估与监控系统（如Prometheus、LangSmith）
- **Day 60**：构建一个监控系统
- **Day 61**：学习多Agent系统设计
- **Day 62**：构建一个多Agent协作系统
- **Day 63**：复习与测试

#### 第15-16周：
- **Day 64-70**：综合项目实战
  - 完成一个完整的大模型应用（如智能客服、文档助手、多模态助手）
  - 撰写项目文档
  - 发布GitHub/部署上线
  - 进行性能优化与迭代

---

## ✅ 每日学习成果检验机制

> **每日学习结束前进行15分钟自我测试：**

- **Prompt工程**：能否写出一个有效Prompt并解释其设计逻辑？
- **RAG系统**：是否能独立部署一个RAG系统并解释其流程？
- **函数调用**：是否能设计一个调用本地函数的Agent？
- **模型调用与部署**：是否能使用Ollama或HuggingFace本地调用模型？
- **LangChain/LlamaIndex**：是否能使用其中的Chain或Query Engine？
- **项目实战**：是否每天都有代码产出或文档进展？

---

## 📈 学习效果评估与调整机制

| 学习效果 | 响应机制 |
|----------|----------|
| ✅ 每日任务完成、理解良好 | 给予鼓励，继续推进 |
| ⚠️ 部分内容掌握不牢 | 当天或次日进行复习 + 补充练习 |
| ❌ 多日任务未完成或理解困难 | 暂停当前阶段，回到基础内容复习，重新制定学习节奏 |

---

## 🧩 推荐资源

- **书籍**：
  - 《Prompt Engineering Guide》
  - 《LangChain官方文档》
  - 《LlamaIndex官方文档》

- **平台**：
  - OpenAI API
  - HuggingFace
  - LlamaIndex
  - LangChain
  - FastAPI / Flask
  - Ollama / LM Studio

- **工具**：
  - VSCode + Jupyter Notebook
  - Git + GitHub
  - Docker
  - Streamlit / Gradio

---

## 🎁 结语

你已经具备了成为大模型应用高级开发者的坚实基础。

> **记住：学习是螺旋式上升的过程，遇到困难不要怕，我们一步步来。**

---

需要我每天帮你检验学习成果、调整计划、提供练习题或小测试吗？随时告诉我！😊
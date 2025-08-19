# ai 入门搭建本地机器人
import asyncio
import platform

from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam, ChatCompletionMessageParam,
)

# 导入自定义的LLM配置模块
from llm_config import get_default_llm

# 获取默认的LLM实例
try:
    llm = get_default_llm()
except Exception as e:
    print(f"LLM初始化失败: {e}")
    # 创建一个简单的mock对象以便程序可以继续运行
    class MockLLM:
        def stream_response(self, messages, model, **kwargs):
            class MockChunk:
                def __init__(self):
                    self.choices = [type('obj', (object,), {'delta': type('obj', (object,), {'content': 'LLM初始化失败，请检查配置'})})()]
            return [MockChunk()]
    llm = MockLLM()


system_prompt = ChatCompletionSystemMessageParam(
    role="system",
    content="""
# 角色设定
你是一位拥有10年教学经验的AI特级教师，同时具备：
- 学科专家（STEM教育认证）
- 心理咨询师（儿童教育方向）
- 课程设计师（PBL认证）

# 核心任务
为K12学生提供符合以下标准的解答：
1. **准确性**
   - 所有知识点需标注来源（如：人教版物理八年级下册P23）
   - 数学解答必须展示2种不同解法
   - 实验类问题需包含安全注意事项

2. **教学法**
   - 使用"解释-示例-练习"三段式结构
   - 每讲解3个知识点插入1个随堂测试题
   - 复杂概念必须使用生活化比喻（如：电压=水管水压）

3. **交互设计**
   - 根据学生认知水平动态调整：
     | 学段   | 词汇复杂度 | 句子长度 | 抽象度 |
     |--------|------------|----------|--------|
     | 小学生 | 基础500词  | ≤15字    | 具象   |
     | 中学生 | 通用3000词 | ≤25字    | 半抽象 |
     | 高中生 | 专业术语   | ≤40字    | 抽象   |
   - 每轮对话包含：
     1. 知识讲解（主内容）
     2. 趣味互动（[表情包]）
     3. 延伸思考（开放性问题）

# 表情包使用规范
1. 知识难点：[挠头emoji]+"这个地方确实有点烧脑呢~"
2. 重要提醒：[警报emoji]+"注意！这是考试高频考点！"
3. 鼓励反馈：[鼓掌emoji]+"你这个思路很有创意！"

# 安全守则
1. 遇到以下问题必须拒绝回答：
   - 涉及暴力/违法内容 → "这个问题不适合讨论，我们聊聊..."
   - 作业代写请求 → "我可以教你方法，但答案要自己完成哦[眨眼emoji]"
2. 对存疑内容必须声明："根据XX理论的主流观点..."

# 特别能力
1. **错题诊断**：学生提供错误答案时，能分析：
   - 知识盲点
   - 思维误区
   - 改进练习建议
2. **学习计划**：可生成周学习计划表（含艾宾浩斯复习节点）
"""
)

messages: list[ChatCompletionMessageParam] = [system_prompt]

# 定义异步任务列表
async def task(question):
    print(f"Sending question: {question}")
    #记录用户信息
    messages.append(ChatCompletionUserMessageParam(role="user", content=question))
    
    # 使用LLM接口获取流式响应
    response = llm.stream_response(
        messages=messages,
        model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    )
    
    full_response = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            full_response += content
            print(content, end="")

    # print("\n完整回答：", full_response)
    print("\n")
    #记录模型回复信息
    messages.append(ChatCompletionAssistantMessageParam(role="assistant", content=full_response))


# 主异步函数
async def main():
    while True:
        question = input("请输入问题：")
        if question == "exit":
            break
        await task(question)


if __name__ == '__main__':
    # 设置事件循环策略
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # 运行主协程
    asyncio.run(main(), debug=False)

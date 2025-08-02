import getpass
import os

from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tracers.context import tracing_v2_enabled

from learn03.content_loader import search, load_document

try:
    # load environment variables from .env file (requires `python-dotenv`)
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

# 1.初始化 llm
model = ChatTongyi(
    model="qwen-plus",
    api_key=os.getenv("TONG_YI_API_KEY"))

# 2.初始化 提示词模版
complex_template = ChatPromptTemplate.from_messages([
    ("system", """
你是一名高级ai开发教练，你严谨，认证细致，幽默。你的主要职责是 
1. 帮助制定学习计划
2. 检验每日的学习成果，并针对学习效果进行评估。
3. 当学习效果较好时，给予鼓励，当学习效果 较差时 针对不足的内容提出针对性的学习方案，并在此检验直到完成
4. 能够根据实际情况动态调整学习计划与目标。
5. 每次会带 以markdown 格式输出
6. 我的学习计划是{plan}
7. 我当前的学习内容有{learn}
8. 你可以基于当前包含的内容回答问题，当你不知道的时候可以回答不知道
"""),
    ("user", "{query}"),
])

# 3.通过向量数据库检索出相关数据 ，并结合用户问题，生成最终的回答
with tracing_v2_enabled(project_name=os.environ["LANGSMITH_PROJECT"]):
    response = model.invoke(complex_template.invoke({"plan": search("学习计划"), "learn": search("学习内容"),"query":"7.20 学习情况"}))
    print(response.content)

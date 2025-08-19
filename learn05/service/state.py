from pydantic import BaseModel


class WorkflowState(BaseModel):
    """
    工作流状态模型
    """
    natural_language: str
    sql_query: str = ""
    result: str = ""
    explanation: str = ""

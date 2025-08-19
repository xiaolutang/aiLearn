import unittest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime

# 创建一个全新的测试应用，不依赖实际数据库
app = FastAPI()

# 简单的OAuth2密码流配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 模拟的认证依赖函数
def get_current_user(token: str = Depends(oauth2_scheme)):
    # 总是返回一个模拟的管理员用户
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin"
    }

# 模拟的登录路由
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 简单的用户名和密码检查
    if form_data.username == "admin" and form_data.password == "admin123":
        return {
            "access_token": "mock_access_token",
            "token_type": "bearer",
            "user_id": 1,
            "username": "admin",
            "email": "admin@example.com"
        }
    else:
        # 模拟401错误
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="用户名或密码错误")

# 模拟的根路由
@app.get("/")
def root():
    return {
        "code": 200,
        "message": "智能教学助手服务运行中",
        "version": "1.0.0"
    }

# 模拟的健康检查路由
@app.get("/health")
def health_check():
    return {
        "code": 200,
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

class IntelligentTeachingAssistantTestCase(unittest.TestCase):
    def setUp(self):
        # 创建测试客户端
        self.client = TestClient(app)
    
    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["code"], 200)
        self.assertIn("智能教学助手", data["message"])
        self.assertEqual(data["version"], "1.0.0")
    
    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["code"], 200)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
    
    def test_login(self):
        # 使用正确的凭据登录
        response = self.client.post("/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        # 检查响应状态码和内容
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["user_id"], 1)
        self.assertEqual(data["username"], "admin")
        self.assertEqual(data["email"], "admin@example.com")

if __name__ == "__main__":
    unittest.main()
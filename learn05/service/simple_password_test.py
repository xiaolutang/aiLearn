import bcrypt
from database import SessionLocal, User

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

db = SessionLocal()
user = db.query(User).filter(User.username == 'admin01').first()
if user:
    print('用户:', user.username)
    print('数据库密码哈希:', user.password[:50] + '...')
    result = verify_password('Admin01!', user.password)
    print('验证Admin01!:', result)
else:
    print('未找到用户')
db.close()
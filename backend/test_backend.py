"""
快速测试后端是否正常工作
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
import time

print("=" * 50)
print("测试后端连接")
print("=" * 50)

# 测试健康检查
try:
    print("\n1. 测试健康检查接口...")
    response = requests.get("http://127.0.0.1:8001/health", timeout=5)
    if response.status_code == 200:
        print(f"[OK] Health check: {response.json()}")
    else:
        print(f"[FAIL] Status code: {response.status_code}")
except Exception as e:
    print(f"[ERROR] {e}")
    print("\n请先启动后端：uvicorn main:app --port 8001")
    sys.exit(1)

# 测试登录接口
try:
    print("\n2. 测试登录接口...")
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/auth/login",
        json={
            "employee_id": "admin001",
            "password": "admin123"
        },
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Login successful!")
        print(f"  User: {data.get('user', {}).get('name')}")
        print(f"  Token: {data.get('access_token', '')[:50]}...")
    else:
        print(f"[FAIL] Status code: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)

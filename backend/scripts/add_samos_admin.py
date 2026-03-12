
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import hashlib
from app.core.database import SessionLocal
from app.db.models import User

# 创建数据库连接
db = SessionLocal()

try:
    # 检查用户是否存在
    existing = db.query(User).filter(User.employee_id == "samos").first()

    if existing:
        # 更新现有用户
        existing.hashed_password = hashlib.sha256("137900".encode()).hexdigest()
        existing.role = "admin"
        existing.is_active = True
        existing.name = "Samos"
        existing.department = "IT部门"
        print("✅ 用户 samos 已存在，已更新为管理员权限")
    else:
        # 创建新用户
        admin = User(
            employee_id="samos",
            name="Samos",
            department="IT部门",
            hashed_password=hashlib.sha256("137900".encode()).hexdigest(),
            role="admin",
            is_active=True
        )
        db.add(admin)
        print("✅ 管理员用户 samos 创建成功")

    db.commit()

    print("\n" + "="*50)
    print("管理员账号信息")
    print("="*50)
    print("工号: samos")
    print("密码: 137900")
    print("姓名: Samos")
    print("角色: admin")
    print("="*50)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

input("\n按回车键退出...")
快速添加 samos 管理员
直接运行此脚本即可添加管理员账号 """

# -*- coding: utf-8 -*-
"""
快速添加 samos 管理员
直接运行此脚本即可添加管理员账号
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
        print("[OK] User samos already exists, updated to admin")
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
        print("[OK] Admin user samos created successfully")

    db.commit()

    print("\n" + "="*50)
    print("Admin Account Info")
    print("="*50)
    print("Employee ID: samos")
    print("Password: 137900")
    print("Name: Samos")
    print("Role: admin")
    print("="*50)

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\nAdmin account created/updated successfully!")

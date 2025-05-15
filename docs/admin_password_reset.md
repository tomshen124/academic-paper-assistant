# 管理员密码重置指南

本文档提供了重置管理员密码的步骤和说明。

## 1. 使用密码重置脚本

我们提供了一个专门的脚本来重置管理员密码，该脚本位于 `/edu-kg/scripts/reset_admin_password_pg.py`。

### 1.1 脚本使用方法

```bash
# 使用默认密码 "admin123" 重置
cd /edu-kg
python scripts/reset_admin_password_pg.py

# 使用自定义密码重置
cd /edu-kg
python scripts/reset_admin_password_pg.py your_new_password
```

### 1.2 脚本工作原理

该脚本会执行以下操作：

1. 连接到 PostgreSQL 数据库
2. 检查用户表中是否存在管理员用户
3. 如果存在，更新管理员密码
4. 如果不存在，创建一个新的管理员用户

脚本会生成详细的日志，帮助诊断可能出现的问题。

## 2. 手动重置密码

如果脚本无法正常工作，您可以手动重置密码：

### 2.1 使用 PostgreSQL 命令行

```bash
# 连接到数据库
psql -U postgres -d academic_paper_assistant

# 更新管理员密码（使用预先生成的哈希值）
UPDATE users SET hashed_password = '$2b$12$your_bcrypt_hash' WHERE username = 'admin';

# 退出
\q
```

### 2.2 生成 bcrypt 哈希值

您可以使用以下 Python 代码生成 bcrypt 哈希值：

```python
import bcrypt

def get_password_hash(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

# 生成哈希值
password = "your_new_password"
hashed_password = get_password_hash(password)
print(hashed_password)
```

## 3. 常见问题

### 3.1 脚本报错：无法连接到数据库

**问题**：脚本无法连接到数据库。

**解决方案**：
- 检查数据库连接信息是否正确
- 确认 PostgreSQL 服务是否正在运行
- 检查防火墙设置是否允许连接
- 确认数据库用户有足够的权限

### 3.2 密码重置成功但无法登录

**问题**：密码重置成功，但仍然无法登录。

**解决方案**：
- 检查日志文件获取详细错误信息
- 确认前端使用的API端点是否正确
- 检查JWT密钥是否一致
- 尝试清除浏览器缓存和Cookie

### 3.3 bcrypt哈希生成错误

**问题**：生成bcrypt哈希时出错。

**解决方案**：
- 确认已安装bcrypt库：`pip install bcrypt`
- 确认密码是有效的字符串
- 检查Python版本是否兼容

## 4. 安全建议

1. 重置密码后立即更改默认密码
2. 使用强密码（至少12个字符，包含大小写字母、数字和特殊字符）
3. 定期更换密码
4. 限制对重置脚本的访问
5. 在生产环境中，考虑实现更安全的密码重置机制，如电子邮件验证

## 5. 相关文件

- `/edu-kg/scripts/reset_admin_password_pg.py`：PostgreSQL数据库密码重置脚本
- `/edu-kg/backend/app/core/security.py`：密码哈希和验证函数
- `/edu-kg/backend/app/api/v1/endpoints/auth.py`：认证API端点

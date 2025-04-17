from app.db.session import SessionLocal
from app.models.token_usage import TokenUsage

db = SessionLocal()
count = db.query(TokenUsage).count()
print('TokenUsage表中的记录数:', count)

if count > 0:
    print('最新的5条记录:')
    records = db.query(TokenUsage).order_by(TokenUsage.timestamp.desc()).limit(5).all()
    for r in records:
        print(f'ID: {r.id}, 用户ID: {r.user_id}, 模型: {r.model}, 服务: {r.service}, 总tokens: {r.total_tokens}, 时间: {r.timestamp}')

"""
添加 UserSession 表

修复 "数据库连接错误" 问题：
UserSession 模型未在数据库中，导致查询失败。
"""
from sqlalchemy import text

def upgrade():
    """升级数据库结构"""
    # 添加 is_active 列到 UserSession 表
    text("""
        ALTER TABLE user_sessions
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE;
        
        -- 添加索引
        CREATE INDEX IF NOT EXISTS ix_user_sessions_user_id ON user_sessions(user_id);
        CREATE INDEX IF NOT EXISTS ix_user_sessions_token_id ON user_sessions(token_id);
        CREATE INDEX IF NOT EXISTS ix_user_sessions_is_active ON user_sessions(is_active);
        
        -- 更新现有数据
        UPDATE user_sessions SET user_id = (
            SELECT u.id FROM users u 
            WHERE u.id = (
                SELECT us.user_id 
                FROM user_sessions us
                WHERE us.user_id IS NULL 
                LIMIT 1
            )
        ) 
        WHERE user_sessions.user_id IS NULL;
        
        -- 创建外键约束
        ALTER TABLE user_sessions DROP CONSTRAINT IF EXISTS user_sessions_user_id_fkey;
        ALTER TABLE user_sessions 
        ADD CONSTRAINT user_sessions_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    """)
    
    print(text)

def downgrade():
    """降级数据库结构"""
    text("""
        -- 移除外键约束
        ALTER TABLE user_sessions DROP CONSTRAINT IF EXISTS user_sessions_user_id_fkey;
        
        -- 移除索引
        DROP INDEX IF EXISTS ix_user_sessions_is_active;
        DROP INDEX IF EXISTS ix_user_sessions_user_id;
        DROP INDEX IF EXISTS ix_user_sessions_token_id;
        DROP INDEX IF EXISTS ix_user_sessions_user_id;
        
        -- 移除 is_active 列
        ALTER TABLE user_sessions DROP COLUMN IF EXISTS is_active;
    """)
    
    print(text)

if __name__ == "__main__":
    print("=== 数据库迁移脚本已生成 ===")
    print("SQL 命令：")
    print("  1. 添加 is_active 列到 UserSession 表")
    print("  2. 添加 user_id 外键约束")
    print("  3. 添加必要的索引")
    print("  4. 更新现有数据的 user_id")
    print("  5. 创建外键约束")

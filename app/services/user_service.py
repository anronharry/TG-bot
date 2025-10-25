"""
User service for user management and permissions
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models.schema import User, Group, GroupAuthorizedUser, UserAPIKey
from app.core.redis_client import redis_client
from app.core.security import security_manager


class UserService:
    """Service for user management and permissions"""
    
    async def get_or_create_user(
        self, 
        session: AsyncSession, 
        user_id: int, 
        username: Optional[str] = None, 
        first_name: str = "Unknown"
    ) -> User:
        """Get existing user or create new one"""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                id=user_id,
                username=username,
                first_name=first_name
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        
        return user
    
    async def is_user_banned(self, session: AsyncSession, user_id: int) -> bool:
        """Check if user is banned (with Redis cache)"""
        cache_key = f"user_perms:{user_id}"
        
        # Try Redis cache first
        cached = await redis_client.get(cache_key)
        if cached is not None:
            return cached == "banned"
        
        # Fallback to database
        stmt = select(User.is_banned).where(User.id == user_id)
        result = await session.execute(stmt)
        is_banned = result.scalar_one_or_none() or False
        
        # Cache the result
        await redis_client.set(cache_key, "banned" if is_banned else "active", ex=300)
        return is_banned
    
    async def ban_user(self, session: AsyncSession, user_id: int) -> bool:
        """Ban a user"""
        stmt = update(User).where(User.id == user_id).values(is_banned=True)
        result = await session.execute(stmt)
        await session.commit()
        
        # Clear cache
        await redis_client.delete(f"user_perms:{user_id}")
        
        return result.rowcount > 0
    
    async def unban_user(self, session: AsyncSession, user_id: int) -> bool:
        """Unban a user"""
        stmt = update(User).where(User.id == user_id).values(is_banned=False)
        result = await session.execute(stmt)
        await session.commit()
        
        # Clear cache
        await redis_client.delete(f"user_perms:{user_id}")
        
        return result.rowcount > 0
    
    async def set_user_model(self, session: AsyncSession, user_id: int, model_id: int) -> bool:
        """Set user's selected AI model"""
        # 对于个人自定义模型（ID >= 10000），我们需要特殊处理
        # 因为外键约束要求 selected_model_id 必须存在于 ai_models 表中
        if model_id >= 10000:
            # 个人自定义模型：暂时设置为 NULL，在 AI 处理时通过特殊逻辑处理
            stmt = update(User).where(User.id == user_id).values(selected_model_id=None)
            result = await session.execute(stmt)
            await session.commit()
            
            # 将个人自定义模型ID存储到Redis中作为临时解决方案
            custom_model_key = f"user_custom_model:{user_id}"
            await redis_client.set(custom_model_key, str(model_id))
            return result.rowcount > 0
        else:
            # 全局模型：正常处理
            stmt = update(User).where(User.id == user_id).values(selected_model_id=model_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
    
    async def get_user_model(self, session: AsyncSession, user_id: int) -> Optional[int]:
        """Get user's selected AI model ID"""
        # 首先检查是否有个人自定义模型
        custom_model_key = f"user_custom_model:{user_id}"
        custom_model_id = await redis_client.get(custom_model_key)
        if custom_model_id:
            return int(custom_model_id)
        
        # 如果没有个人自定义模型，检查全局模型
        stmt = select(User.selected_model_id).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def set_user_api_key(
        self, 
        session: AsyncSession, 
        user_id: int, 
        model_id: int, 
        api_key: str
    ) -> bool:
        """Set user's custom API key for a model"""
        encrypted_key = security_manager.encrypt(api_key)
        
        # Use PostgreSQL upsert
        stmt = pg_insert(UserAPIKey).values(
            user_id=user_id,
            model_id=model_id,
            encrypted_api_key=encrypted_key
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=['user_id', 'model_id'],
            set_=dict(encrypted_api_key=encrypted_key)
        )
        
        await session.execute(stmt)
        await session.commit()
        return True
    
    async def is_user_authorized_in_group(self, session: AsyncSession, user_id: int, group_id: int) -> bool:
        """Check if user is authorized in group (with Redis cache)"""
        cache_key = f"group_auth:{group_id}"
        
        # Try Redis cache first
        cached_users = await redis_client.get_json(cache_key)
        if cached_users is not None:
            return str(user_id) in cached_users
        
        # Fallback to database
        stmt = select(GroupAuthorizedUser.user_id).where(
            GroupAuthorizedUser.group_id == group_id
        )
        result = await session.execute(stmt)
        authorized_users = [str(row[0]) for row in result.fetchall()]
        
        # Cache the result
        await redis_client.set_json(cache_key, authorized_users, ex=300)
        return str(user_id) in authorized_users
    
    async def authorize_user_in_group(
        self, 
        session: AsyncSession, 
        group_id: int, 
        user_id: int, 
        authorized_by: int
    ) -> bool:
        """Authorize user in group"""
        # First, ensure group exists
        group_stmt = select(Group).where(Group.id == group_id)
        group_result = await session.execute(group_stmt)
        group = group_result.scalar_one_or_none()
        
        if not group:
            # Create group if it doesn't exist
            group = Group(id=group_id, title=f"Group {group_id}")
            session.add(group)
            await session.flush()
        
        # Add authorization
        auth = GroupAuthorizedUser(
            group_id=group_id,
            user_id=user_id,
            authorized_by=authorized_by
        )
        session.add(auth)
        await session.commit()
        
        # Clear cache
        await redis_client.delete(f"group_auth:{group_id}")
        
        return True
    
    async def revoke_user_from_group(self, session: AsyncSession, group_id: int, user_id: int) -> bool:
        """Revoke user authorization from group"""
        stmt = select(GroupAuthorizedUser).where(
            GroupAuthorizedUser.group_id == group_id,
            GroupAuthorizedUser.user_id == user_id
        )
        result = await session.execute(stmt)
        auth = result.scalar_one_or_none()
        
        if auth:
            await session.delete(auth)
            await session.commit()
            
            # Clear cache
            await redis_client.delete(f"group_auth:{group_id}")
            return True
        
        return False
    
    async def clear_user_context(self, user_id: int) -> None:
        """Clear user's conversation context"""
        context_key = f"context:{user_id}"
        await redis_client.delete(context_key)


# Global user service instance
user_service = UserService()

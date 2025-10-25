"""
用户个人自定义模型服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schema import UserCustomModel
from typing import List, Optional

class UserCustomModelService:
    """用户个人自定义模型服务类"""
    
    async def get_user_custom_models(self, session: AsyncSession, user_id: int) -> List[UserCustomModel]:
        """获取用户的所有个人自定义模型"""
        stmt = select(UserCustomModel).where(
            UserCustomModel.user_id == user_id,
            UserCustomModel.is_active == True
        ).order_by(UserCustomModel.created_at.desc())
        
        result = await session.execute(stmt)
        return result.scalars().all()
    
    async def get_custom_model_by_name(self, session: AsyncSession, user_id: int, custom_name: str) -> Optional[UserCustomModel]:
        """根据自定义名称获取用户的个人自定义模型"""
        stmt = select(UserCustomModel).where(
            UserCustomModel.user_id == user_id,
            UserCustomModel.custom_name == custom_name,
            UserCustomModel.is_active == True
        )
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_custom_model_by_id(self, session: AsyncSession, custom_model_id: int) -> Optional[UserCustomModel]:
        """根据ID获取个人自定义模型"""
        stmt = select(UserCustomModel).where(
            UserCustomModel.id == custom_model_id,
            UserCustomModel.is_active == True
        )
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

# 创建服务实例
user_custom_model_service = UserCustomModelService()

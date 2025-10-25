"""
SQLAlchemy database models
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    """User information table"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    selected_model_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ai_models.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    selected_model: Mapped[Optional["AIModel"]] = relationship(
        "AIModel", 
        foreign_keys=[selected_model_id],
        back_populates="users"  # 修复：添加 back_populates
    )
    api_keys: Mapped[list["UserAPIKey"]] = relationship("UserAPIKey", back_populates="user")
    custom_models: Mapped[list["UserCustomModel"]] = relationship(
        "UserCustomModel", 
        foreign_keys="UserCustomModel.user_id",
        back_populates="user"  # 修复：添加 back_populates
    )
    chat_history: Mapped[list["ChatHistory"]] = relationship("ChatHistory", back_populates="user")
    group_authorizations: Mapped[list["GroupAuthorizedUser"]] = relationship(
        "GroupAuthorizedUser", 
        back_populates="user", 
        foreign_keys="GroupAuthorizedUser.user_id"
    )


class AIModel(Base):
    """AI model configuration table"""
    __tablename__ = "ai_models"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    api_provider: Mapped[str] = mapped_column(String(100), nullable=False)
    api_endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # 新增：全局加密密钥与可选 headers/parameters（JSON）
    encrypted_api_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    headers: Mapped[dict] = mapped_column(JSON, default=dict)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User", 
        foreign_keys="User.selected_model_id",
        back_populates="selected_model"  # 修复：添加 back_populates
    )
    user_api_keys: Mapped[list["UserAPIKey"]] = relationship("UserAPIKey", back_populates="model")


class UserAPIKey(Base):
    """User custom API keys table"""
    __tablename__ = "user_api_keys"
    __table_args__ = (
        UniqueConstraint('user_id', 'model_id', name='uq_user_model_api_key'),
    )
    
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), primary_key=True)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_models.id"), primary_key=True)
    encrypted_api_key: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")
    model: Mapped["AIModel"] = relationship("AIModel", back_populates="user_api_keys")


class UserCustomModel(Base):
    """User's personal custom AI models table"""
    __tablename__ = "user_custom_models"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    custom_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_provider: Mapped[str] = mapped_column(String(100), nullable=False)
    api_endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    encrypted_api_key: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[user_id],
        back_populates="custom_models"  # 修复：添加 back_populates
    )


class Group(Base):
    """Authorized groups information table"""
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    authorized_users: Mapped[list["GroupAuthorizedUser"]] = relationship("GroupAuthorizedUser", back_populates="group")
    chat_history: Mapped[list["ChatHistory"]] = relationship("ChatHistory", back_populates="group")


class GroupAuthorizedUser(Base):
    """Group authorized users table"""
    __tablename__ = "group_authorized_users"
    __table_args__ = (
        UniqueConstraint('group_id', 'user_id', name='uq_group_user_authorization'),
    )
    
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), primary_key=True)
    authorized_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    authorized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    group: Mapped["Group"] = relationship("Group", back_populates="authorized_users")
    user: Mapped["User"] = relationship("User", back_populates="group_authorizations", foreign_keys=[user_id])
    authorizer: Mapped["User"] = relationship("User", foreign_keys=[authorized_by])


class ChatHistory(Base):
    """Chat history table"""
    __tablename__ = "chat_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    group_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("groups.id"), nullable=True)
    message_role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' or 'assistant'
    message_content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_history")
    group: Mapped[Optional["Group"]] = relationship("Group", back_populates="chat_history")
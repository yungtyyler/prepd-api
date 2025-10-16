from typing import List
import uuid
from sqlalchemy import Column, Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base
from passlib.context import CryptContext

# This handles salt generation and encoding automatically.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    # Attributes
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, nullable=False)
    _password_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    recipes: Mapped[List["SavedRecipe"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    meal_plans: Mapped[List["MealPlan"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        self._password_hash = pwd_context.hash(password)
    
    def check_password(self, password):
        return pwd_context.verify(password, self._password_hash)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
    
class SavedRecipe(Base):
    __tablename__ = "saved_recipes"

    # Attributes
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    api_recipe_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[str] = mapped_column(String)
    instructions: Mapped[str] = mapped_column(Text)
    ingredients: Mapped[dict] = mapped_column(JSONB)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey=("users.id"), nullable=False)

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="recipes")
    meal_plan_entries: Mapped[List["MealPlan"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SavedRecipe(id={self.id}, title='{self.title}')>"
    
class MealPlan(Base):
    __tablename__ = "meal_plan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey=("users.id"), nullable=False)
    saved_recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey=("saved_recipes.id"), nullable=False)
    plan_date: Mapped[Date] = mapped_column(Date, nullable=False)

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="meal_plans")
    recipe: Mapped["SavedRecipe"] = relationship(back_populates="meal_plan_entries")

    def __repr__(self):
        return f"<MealPlan(id={self.id}, plan_date='{self.plan_date}')>"
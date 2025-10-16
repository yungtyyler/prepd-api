import datetime
from uuid import UUID
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List

# -- Ingredients ==

class Ingredient(BaseModel):
    ingredient: str
    measure: str

# -- Saved Recipes --

class SavedRecipeBase(BaseModel):
    api_recipe_id: str
    title: str
    image_url: Optional[str] = None
    instructions: Optional[str] = None
    ingredients: Optional[List[Ingredient]] = None

class SavedRecipeCreate(SavedRecipeBase):
    pass

class SavedRecipe(SavedRecipeBase):
    id: int
    user_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

# -- Meal Plans --
class MealPlanBase(BaseModel):
    id: int
    user_id: uuid.UUID
    recipe: SavedRecipe
    model_config = ConfigDict(from_attributes=True)

class MealPlanCreate(MealPlanBase):
    pass

class MealPlan(MealPlanBase):
    pass
    
# -- Users --
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

# IMPORTANT: It does NOT include the password_hash for security.
class User(UserBase):
    id: UUID
    created_at: datetime.datetime
    recipes: List[SavedRecipe] = []
    meal_plans: List[MealPlan] = []
    model_config = ConfigDict(from_attributes=True)
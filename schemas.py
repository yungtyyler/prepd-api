import datetime
from uuid import UUID
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints, constr
from typing import Optional, List, Annotated

# -- TheMealDB Item --
class TheMealDBRecipe(BaseModel):
    idMeal: str
    strMeal: str
    strMealThumb: Optional[str] = None
    strInstructions: Optional[str] = None
    strIngredient1: Optional[str] = None
    strMeasure1: Optional[str] = None
    strIngredient2: Optional[str] = None
    strMeasure2: Optional[str] = None
    strIngredient3: Optional[str] = None
    strMeasure3: Optional[str] = None
    strIngredient4: Optional[str] = None
    strMeasure4: Optional[str] = None
    strIngredient5: Optional[str] = None
    strMeasure5: Optional[str] = None
    strIngredient6: Optional[str] = None
    strMeasure6: Optional[str] = None
    strIngredient7: Optional[str] = None
    strMeasure7: Optional[str] = None
    strIngredient8: Optional[str] = None
    strMeasure8: Optional[str] = None
    strIngredient9: Optional[str] = None
    strMeasure9: Optional[str] = None
    strIngredient10: Optional[str] = None
    strMeasure10: Optional[str] = None
    strIngredient11: Optional[str] = None
    strMeasure11: Optional[str] = None
    strIngredient12: Optional[str] = None
    strMeasure12: Optional[str] = None
    strIngredient13: Optional[str] = None
    strMeasure13: Optional[str] = None
    strIngredient14: Optional[str] = None
    strMeasure14: Optional[str] = None
    strIngredient15: Optional[str] = None
    strMeasure15: Optional[str] = None
    strIngredient16: Optional[str] = None
    strMeasure16: Optional[str] = None
    strIngredient17: Optional[str] = None
    strMeasure17: Optional[str] = None
    strIngredient18: Optional[str] = None
    strMeasure18: Optional[str] = None
    strIngredient19: Optional[str] = None
    strMeasure19: Optional[str] = None
    strIngredient20: Optional[str] = None
    strMeasure20: Optional[str] = None

class TheMealDBResponse(BaseModel):
    meals: Optional[List[TheMealDBRecipe]] = None

# -- Token --
class Token(BaseModel):
    access_token: str
    token_type: str
    
# -- Ingredients --

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
    plan_date: datetime.date
    saved_recipe_id: int

class MealPlanCreate(MealPlanBase):
    pass

class MealPlan(MealPlanBase):
    id: int
    user_id: uuid.UUID
    recipe: SavedRecipe
    model_config = ConfigDict(from_attributes=True)
    
# -- Users --
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=8, max_length=72)]

class UserPublic(UserBase):
    id: UUID
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# IMPORTANT: It does NOT include the password_hash for security.
class User(UserBase):
    id: UUID
    created_at: datetime.datetime
    recipes: List[SavedRecipe] = []
    meal_plans: List[MealPlan] = []
    model_config = ConfigDict(from_attributes=True)

# -- Shopping List --
class ShoppingListItem(BaseModel):
    ingredient: str
    estimated_total: str  # e.g., "3 cups & 1 pinch"
    measures: List[str]   # e.g., ["1 cup", "2 cups", "1 pinch"]
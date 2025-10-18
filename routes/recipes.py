from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import httpx
from database import get_db
import schemas
import models
from sqlalchemy.orm import Session
from routes.auth import get_current_user

router = APIRouter(prefix="/recipes", tags=["Recipes"])

# Define the base URL for TheMealDB API
THEMEALDB_API_URL = "https://www.themealdb.com/api/json/v1/1/search.php"
MAX_INGREDIENTS_PER_MEAL = 20

@router.get("/search", response_model=List[schemas.SavedRecipeBase])
async def search_recipe(query: str, current_user: models.User = Depends(get_current_user)):
    """
    Searches for recipes from TheMealDB API.
    This is a protected endpoint; a valid JWT is required.
    The `Depends(get_current_user)` is our security guard.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{THEMEALDB_API_URL}?s={query}")
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error contacting TheMealDB API: {exc}"
            )
        
    data = response.json()
    meals = data.get("meals")

    if not meals:
        return []
    
    results = []
    for meal in meals:
        ingredients = []
        for i in range(1, MAX_INGREDIENTS_PER_MEAL + 1):
            ingredient_name: str = meal.get(f"strIngredient{i}")
            ingredient_measure: str = meal.get(f"strMeasure{i}")
            if ingredient_name and ingredient_name.strip():
                ingredients.append(schemas.Ingredient(ingredient=ingredient_name, measure=ingredient_measure or ""))
        
        recipe_data = schemas.SavedRecipeBase(
            api_recipe_id=meal['idMeal'],
            image_url=meal['strMealThumb'],
            ingredients=ingredients,
            instructions=meal['strInstructions'],
            title=meal['strMeal']
        )
        results.append(recipe_data)
    
    return results

@router.post("/save", response_model=schemas.SavedRecipe, status_code=status.HTTP_201_CREATED)
def save_recipe(recipe: schemas.SavedRecipeCreate, db: Session=Depends(get_db), current_user: models.User=Depends(get_current_user)):
    """
    Saves a recipe to the logged-in user's collection.
    """
    db_recipe = db.query(models.SavedRecipe).filter(
        models.SavedRecipe.api_recipe_id == recipe.api_recipe_id,
        models.SavedRecipe.user_id == current_user.id
    ).first()

    if db_recipe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have this recipe saved."
        )
    
    new_saved_recipe = models.SavedRecipe(
        **recipe.model_dump(),
        user_id=current_user.id
    )

    db.add(new_saved_recipe)
    db.commit()
    db.refresh(new_saved_recipe)

    return new_saved_recipe

@router.get("/saved", response_model=List[schemas.SavedRecipe])
def get_saved_recipes(current_user: models.User = Depends(get_current_user)):
    """
    Retrieves all recipes saved by the currently logged-in user.
    """
    return current_user.recipes

@router.delete("/saved/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Deletes a specific recipe from the user's collection.
    """
    recipe_to_delete = db.query(models.SavedRecipe).filter(
        models.SavedRecipe.id == recipe_id,
        models.SavedRecipe.user_id == current_user.id,
    ).first()

    if not recipe_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found."
        )
    
    db.delete(recipe_to_delete)
    db.commit()
    
    return
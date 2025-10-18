from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import datetime
import schemas
import models
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/meal-plan", tags=["Meal Plan"])

@router.post("", response_model=schemas.MealPlan, status_code=status.HTTP_201_CREATED)
def create_meal_plan(plan_item: schemas.MealPlanCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Adds a saved recipe to the user's meal plan for a specific date.
    """
    saved_recipe = db.query(models.SavedRecipe).filter(
        models.SavedRecipe.id == plan_item.saved_recipe_id,
        models.SavedRecipe.user_id == current_user.id
    ).first()

    if not saved_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved recipe with id {plan_item.id} not found."
        )
    
    existing_plan_entry = db.query(models.MealPlan).filter(
        models.MealPlan.user_id == current_user.id,
        models.MealPlan.plan_date == plan_item.plan_date,
        models.MealPlan.saved_recipe_id == plan_item.saved_recipe_id
    ).first()

    if existing_plan_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This recipe is already planned for this date."
        )
    
    new_plan_entry = models.MealPlan(
        user_id = current_user.id,
        saved_recipe = plan_item.saved_recipe_id,
        plan_date = plan_item.plan_date
    )

    db.add(new_plan_entry)
    db.commit()
    db.refresh(new_plan_entry)

    return new_plan_entry

@router.get("", response_model=List[schemas.MealPlan])
def get_meal_plans():
    # TODO: Create GET request for meal plans within a specific date range
    pass
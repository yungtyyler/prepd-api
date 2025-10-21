from collections import defaultdict
import re
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, TypedDict, Union
from sqlalchemy.orm import Session
import datetime
import schemas
import models
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/meal-plan", tags=["Meal Plan"])

# Define a precise type for the return value of parse_measurement
class ParsedMeasurement(TypedDict):
    quantity: float
    unit: str

# Update the function signature with the new precise type
def parse_measurement(measure_str: str) -> Union[ParsedMeasurement, None]:
    """
    A helper function to parse a measurement string into a quantity and a unit.
    e.g., "1/2 cup" -> {'quantity': 0.5, 'unit': 'cup'}
    e.g., "2" -> {'quantity': 2.0, 'unit': ''}
    Returns None if it can't be reliably parsed.
    """
    if not measure_str or not measure_str.strip():
        return None

    measure_str = measure_str.lower().strip()
    
    # Handle fractions
    fraction_match = re.match(r'(\d+)\s*/\s*(\d+)', measure_str)
    if fraction_match:
        num, den = map(int, fraction_match.groups())
        quantity = num / den
        unit = measure_str[fraction_match.end():].strip()
        return {"quantity": quantity, "unit": unit}

    # Handle numbers (integers or decimals)
    number_match = re.match(r'(\d+\.?\d*)', measure_str)
    if number_match:
        quantity = float(number_match.group(1))
        unit = measure_str[number_match.end():].strip()
        return {"quantity": quantity, "unit": unit}

    return None

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
            detail=f"Saved recipe with id {plan_item.saved_recipe_id} not found."
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
        saved_recipe_id = plan_item.saved_recipe_id,
        plan_date = plan_item.plan_date
    )

    db.add(new_plan_entry)
    db.commit()
    db.refresh(new_plan_entry)

    return new_plan_entry

@router.get("", response_model=List[schemas.MealPlan])
def get_meal_plans(
    start_date: datetime.date,
    end_date: datetime.date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieves all meal plan entries for the current user within a given date range.
    """
    meal_plans = db.query(models.MealPlan).filter(
        models.MealPlan.plan_date >= start_date,
        models.MealPlan.plan_date <= end_date,
        models.MealPlan.user_id == current_user.id
    ).all()

    return meal_plans

@router.delete("/{meal_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_meal_plan(
    meal_plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Removes a recipe from a specific date on their meal planner
    """
    meal_plan_to_delete = db.query(models.MealPlan).filter(
        models.MealPlan.user_id == current_user.id,
        models.MealPlan.id == meal_plan_id
    ).first()

    if not meal_plan_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {meal_plan_id} not found."
        )
    
    db.delete(meal_plan_to_delete)
    db.commit()

    return

@router.get("/shopping-list", response_model=List[schemas.ShoppingListItem])
def get_shopping_list(
    start_date: datetime.date,
    end_date: datetime.date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generates a consolidated shopping list with "best-effort" ingredient aggregation.
    """
    meal_plans = db.query(models.MealPlan).filter(
        models.MealPlan.user_id == current_user.id,
        models.MealPlan.plan_date >= start_date,
        models.MealPlan.plan_date <= end_date
    ).all()

    summed_totals = defaultdict(lambda: defaultdict(float))
    unparsed_measures = defaultdict(list)
    original_measures = defaultdict(list)

    for plan in meal_plans:
        if not plan.recipe.ingredients:
            continue
        for item in plan.recipe.ingredients:
            ingredient_name = item['ingredient'].strip().title()
            measure_str = item['measure']

            if not measure_str or not measure_str.strip():
                continue

            original_measures[ingredient_name].append(measure_str)
            
            parsed = parse_measurement(measure_str)
            if parsed:
                summed_totals[ingredient_name][parsed['unit']] += parsed['quantity']
            else:
                unparsed_measures[ingredient_name].append(measure_str)

    shopping_list = []
    all_ingredients = set(original_measures.keys())

    for ingredient in sorted(list(all_ingredients)):
        total_parts = []
        
        for unit, total in summed_totals.get(ingredient, {}).items():
            # Format to avoid unnecessary .0 (e.g., show "3" instead of "3.0")
            quantity_str = f"{total:g}"
            total_parts.append(f"{quantity_str} {unit}".strip())
        
        # Add any un-parsable measures to the estimated total string
        total_parts.extend(unparsed_measures.get(ingredient, []))

        # Join all parts for a comprehensive total, e.g., "3 cup & 1 pinch"
        estimated_total_str = " & ".join(sorted(total_parts))

        if not estimated_total_str:
            continue

        shopping_list.append(
            schemas.ShoppingListItem(
                ingredient=ingredient,
                estimated_total=estimated_total_str,
                measures=original_measures[ingredient] # The original, un-aggregated list
            )
        )

    return shopping_list
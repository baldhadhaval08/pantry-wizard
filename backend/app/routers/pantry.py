"""Pantry management routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.auth import get_current_user
from app.models import User, PantryItem
from app.schemas import PantryItemCreate, PantryItemUpdate, PantryItemResponse

router = APIRouter(prefix="/pantry", tags=["pantry"])


@router.get("", response_model=List[PantryItemResponse])
async def list_pantry_items(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all pantry items for the current user.
    
    Returns a list of all ingredients in the user's pantry.
    """
    statement = select(PantryItem).where(PantryItem.user_id == current_user.id)
    items = session.exec(statement).all()
    return [PantryItemResponse(**item.model_dump()) for item in items]


@router.post("", response_model=PantryItemResponse, status_code=status.HTTP_201_CREATED)
async def add_pantry_item(
    item_data: PantryItemCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Add a new item to the pantry.
    
    Creates a new pantry item with name, quantity, and unit.
    """
    item = PantryItem(
        user_id=current_user.id,
        name=item_data.name,
        quantity=item_data.quantity,
        unit=item_data.unit
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return PantryItemResponse(**item.model_dump())


@router.put("/{item_id}", response_model=PantryItemResponse)
async def update_pantry_item(
    item_id: int,
    item_data: PantryItemUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update an existing pantry item.
    
    Updates name, quantity, or unit of a pantry item.
    """
    statement = select(PantryItem).where(
        PantryItem.id == item_id,
        PantryItem.user_id == current_user.id
    )
    item = session.exec(statement).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pantry item not found"
        )
    
    if item_data.name is not None:
        item.name = item_data.name
    if item_data.quantity is not None:
        item.quantity = item_data.quantity
    if item_data.unit is not None:
        item.unit = item_data.unit
    
    session.add(item)
    session.commit()
    session.refresh(item)
    return PantryItemResponse(**item.model_dump())


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pantry_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a pantry item.
    
    Removes an item from the user's pantry.
    """
    statement = select(PantryItem).where(
        PantryItem.id == item_id,
        PantryItem.user_id == current_user.id
    )
    item = session.exec(statement).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pantry item not found"
        )
    
    session.delete(item)
    session.commit()
    return None


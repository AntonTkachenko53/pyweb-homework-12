from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from dependencies.auth import get_current_user_email
from dependencies.database import get_db, SessionLocal
from schemas.contacts_schemas import Contact, ContactCreate, ContactUpdate
from services.contacts_service import ContactService
from services.user_service import UserService

router = APIRouter()


@router.get('/')
async def list_contacts(first_name: Optional[str] = None, last_name: Optional[str] = None,
                        email: Optional[str] = None, current_email: str = Depends(get_current_user_email),
                        db: SessionLocal = Depends(get_db)) -> List[Contact]:
    user_service = UserService(db=db)
    user = user_service.get_by_email(current_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email from token')
    else:
        contact_service = ContactService(db=db)
        result = []
        if first_name:
            contact = await contact_service.get_by_first_name(first_name, current_email)
            result.append(contact)
        elif last_name:
            contact = await contact_service.get_by_last_name(last_name, current_email)
            result.append(contact)
        elif email:
            contact = await contact_service.get_by_email(email, current_email)
            result.append(contact)
        else:
            contact = await contact_service.get_all_contacts(current_email)
            result.append(contact)
        return result


@router.get('/{id}')
async def get_contact_by_id(id: int, db: SessionLocal = Depends(get_db),
                            current_email: str = Depends(get_current_user_email)) -> Contact:
    contact_item = await ContactService(db=db).get_by_id(id, current_email)
    return contact_item


@router.post('/')
async def create_contact(contact_item: ContactCreate, db: SessionLocal = Depends(get_db),
                         current_email: str = Depends(get_current_user_email)) -> Contact:
    new_contact = await ContactService(db=db).create_contact(contact_item, current_email)
    return new_contact


@router.put('/{id}')
async def update_contact(id: int, contact_item: ContactUpdate, db: SessionLocal = Depends(get_db),
                         current_email: str = Depends(get_current_user_email)) -> Contact:
    updated_contact = await ContactService(db=db).update(id, contact_item, current_email)
    return updated_contact


@router.delete('/{id}')
async def delete_contact(id: int, db: SessionLocal = Depends(get_db),
                         current_email: str = Depends(get_current_user_email)) -> Contact:
    removed_contact = await ContactService(db=db).remove(id, current_email)
    return removed_contact


@router.get('/birthdays_in_7_days')
async def contacts_birthdays_in_7_days(db: SessionLocal = Depends(get_db),
                                       current_email: str = Depends(get_current_user_email)) -> list[Contact]:
    contacts = ContactService(db=db).contacts_birthdays_in_7_days(current_email)
    return contacts

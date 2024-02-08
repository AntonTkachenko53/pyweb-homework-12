from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from dependencies.auth import get_current_user_email
from dependencies.database import get_db, SessionLocal
from depenedencies.rate_limiter import rate_limit
from schemas.contacts_schemas import Contact, ContactCreate, ContactUpdate
from services.contacts_service import ContactService
from services.user_service import UserService

router = APIRouter()


@router.get('/')
async def list_contacts(first_name: Optional[str] = None, last_name: Optional[str] = None,
                        email: Optional[str] = None, current_email: str = Depends(get_current_user_email),
                        db: SessionLocal = Depends(get_db), rl=Depends(rate_limit)) -> List[Contact]:
    """
    Retrieve a list of contacts based on specified criteria.

    :param first_name: Filter by first name.
    :type first_name: str, optional
    :param last_name: Filter by last name.
    :type last_name: str, optional
    :param email: Filter by email.
    :type email: str, optional
    :param current_email: The email of the current user.
    :type current_email: str
    :param db: Database session dependency.
    :type db: SessionLocal
    :param rl: Rate limit dependency.
    :type rl: RateLimiter
    :return: A list of contacts matching the criteria.
    :rtype: List[Contact]
    """
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
                            current_email: str = Depends(get_current_user_email), rl=Depends(rate_limit)) -> Contact:
    """
    Retrieve a contact by its ID.

    :param id: The ID of the contact to retrieve.
    :type id: int
    :param db: Database session dependency.
    :type db: SessionLocal
    :param current_email: The email of the current user.
    :type current_email: str
    :param rl: Rate limit dependency.
    :type rl: RateLimiter
    :return: The contact with the specified ID.
    :rtype: Contact
    """
    contact_item = await ContactService(db=db).get_by_id(id, current_email)
    return contact_item


@router.post('/')
async def create_contact(contact_item: ContactCreate, db: SessionLocal = Depends(get_db),
                         current_email: str = Depends(get_current_user_email), rl=Depends(rate_limit)) -> Contact:
    """
    Create a new contact.

    :param contact_item: Data for the new contact.
    :type contact_item: ContactCreate
    :param db: Database session dependency.
    :type db: SessionLocal
    :param current_email: The email of the current user.
    :type current_email: str
    :param rl: Rate limit dependency.
    :type rl: RateLimiter
    :return: The newly created contact.
    :rtype: Contact
    """
    new_contact = await ContactService(db=db).create_contact(contact_item, current_email)
    return new_contact


@router.put('/{id}')
async def update_contact(id: int, contact_item: ContactUpdate, db: SessionLocal = Depends(get_db),
                         current_email: str = Depends(get_current_user_email), rl=Depends(rate_limit)) -> Contact:
    """
    Update an existing contact.

    :param id: The ID of the contact to update.
    :type id: int
    :param contact_item: Updated data for the contact.
    :type contact_item: ContactUpdate
    :param db: Database session dependency.
    :type db: SessionLocal
    :param current_email: The email of the current user.
    :type current_email: str
    :param rl: Rate limit dependency.
    :type rl: RateLimiter
    :return: The updated contact.
    :rtype: Contact
    """
    updated_contact = await ContactService(db=db).update(id, contact_item, current_email)
    return updated_contact


@router.delete('/{id}')
async def delete_contact(id: int, db: SessionLocal = Depends(get_db),
                         current_email: str = Depends(get_current_user_email), rl=Depends(rate_limit)) -> Contact:
    """
    Delete a contact.

    :param id: The ID of the contact to delete.
    :type id: int
    :param db: Database session dependency.
    :type db: SessionLocal
    :param current_email: The email of the current user.
    :type current_email: str
    :param rl: Rate limit dependency.
    :type rl: RateLimiter
    :return: The removed contact.
    :rtype: Contact
    """
    removed_contact = await ContactService(db=db).remove(id, current_email)
    return removed_contact


@router.get('/birthdays_in_7_days')
async def contacts_birthdays_in_7_days(db: SessionLocal = Depends(get_db),
                                       current_email: str = Depends(get_current_user_email),
                                       rl=Depends(rate_limit)) -> list[Contact]:
    """
    Retrieve contacts with birthdays in the next 7 days.

    :param db: Database session dependency.
    :type db: SessionLocal
    :param current_email: The email of the current user.
    :type current_email: str
    :param rl: Rate limit dependency.
    :type rl: RateLimiter
    :return: Contacts with birthdays in the next 7 days.
    :rtype: list[Contact]
    """
    contacts = ContactService(db=db).contacts_birthdays_in_7_days(current_email)
    return contacts

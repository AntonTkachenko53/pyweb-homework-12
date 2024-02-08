from repository.contacts_repo import ContactsRepo
from schemas.contacts_schemas import Contact, ContactCreate, ContactUpdate
from models.contacts_model import ContactModel


class ContactService():
    """
    Service class for managing contacts.
    """

    def __init__(self, db):
        """
        Initialize the ContactService instance.

        :param db: A database session.
        :type db: SessionLocal
        """
        self.repo = ContactsRepo(db=db)

    async def get_all_contacts(self, user_email) -> list[Contact]:
        """
        Retrieve all contacts for a specific user.

        :param user_email: The email of the user.
        :type user_email: str
        :return: List of contacts.
        :rtype: list[Contact]
        """
        all_contacts_from_db = await self.repo.get_all(user_email)
        return [Contact.from_orm(item) for item in all_contacts_from_db]

    async def get_by_id(self, id: int, user_email) -> Contact:
        """
        Retrieve a contact by its ID for a specific user.

        :param id: The ID of the contact to retrieve.
        :type id: int
        :param user_email: The email of the user.
        :type user_email: str
        :return: The retrieved contact.
        :rtype: Contact
        """
        contact = await self.repo.get_by_id(id, user_email)
        return Contact.from_orm(contact)

    async def create_contact(self, contact_item: ContactCreate, user_email) -> Contact:
        """
        Create a new contact for a specific user.

        :param contact_item: The contact data to create.
        :type contact_item: ContactCreate
        :param user_email: The email of the user.
        :type user_email: str
        :return: The newly created contact.
        :rtype: Contact
        """
        new_contact_for_db = await self.repo.create(contact_item, user_email)
        return Contact.from_orm(new_contact_for_db)

    async def update(self, contact_item: ContactUpdate, id: int, user_email):
        """
        Update an existing contact for a specific user.

        :param contact_item: The updated contact data.
        :type contact_item: ContactUpdate
        :param id: The ID of the contact to update.
        :type id: int
        :param user_email: The email of the user.
        :type user_email: str
        :return: The updated contact.
        :rtype: Contact
        """
        updated_contact = await self.repo.update(id, contact_item, user_email)
        return Contact.from_orm(updated_contact)

    async def remove(self, id: int, user_email):
        """
        Remove a contact for a specific user.

        :param id: The ID of the contact to remove.
        :type id: int
        :param user_email: The email of the user.
        :type user_email: str
        :return: The removed contact.
        :rtype: Contact
        """
        removed_contact = await self.repo.remove(id, user_email)
        return Contact.from_orm(removed_contact)

    async def get_by_first_name(self, first_name: str, user_email):
        """
        Retrieve a contact by first name for a specific user.

        :param first_name: The first name of the contact.
        :type first_name: str
        :param user_email: The email of the user.
        :type user_email: str
        :return: The retrieved contact.
        :rtype: Contact
        """
        contact = await self.repo.get_by_first_name(first_name, user_email)
        return Contact.from_orm(contact)

    async def get_by_last_name(self, last_name: str, user_email):
        """
        Retrieve a contact by last name for a specific user.

        :param last_name: The last name of the contact.
        :type last_name: str
        :param user_email: The email of the user.
        :type user_email: str
        :return: The retrieved contact.
        :rtype: Contact
        """
        contact = await self.repo.get_by_last_name(last_name, user_email)
        return Contact.from_orm(contact)

    async def get_by_email(self, email: str, user_email):
        """
        Retrieve a contact by email for a specific user.

        :param email: The email of the contact.
        :type email: str
        :param user_email: The email of the user.
        :type user_email: str
        :return: The retrieved contact.
        :rtype: Contact
        """
        contact = await self.repo.get_by_email(email, user_email)
        return Contact.from_orm(contact)

    async def contacts_birthdays_in_7_days(self, user_email):
        """
        Retrieve contacts with birthdays in the next 7 days for a specific user.

        :param user_email: The email of the user.
        :type user_email: str
        :return: List of contacts with upcoming birthdays.
        :rtype: list[Contact]
        """
        contacts = await self.repo.contacts_birthdays_in_7_days(user_email)
        return [Contact.from_orm(item) for item in contacts]

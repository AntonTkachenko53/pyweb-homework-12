from datetime import date, timedelta

from contacts.models.contacts_model import ContactModel


class ContactsRepo():
    """
    A repository for managing user data.

    :param db: A database session.
    :type db: sqlalchemy.orm.session.Session
    """

    def __init__(self, db):
        """
        Initialize the UserRepo instance.

        :param db: A database session.
        :type db: sqlalchemy.orm.session.Session
        """
        self.db = db

    async def get_all(self, user_email):
        """
        Retrieves a list of contacts for a specific user

        :param user_email: users email
        :type user_email: str
        :return: A list of contacts
        :rtype: List[ContactModel]
        """
        return self.db.query(ContactModel).filter(ContactModel.user_email == user_email).all()

    async def create(self, contact_item, user_email):
        """
        Create a new contact for a specific user

        :param contact_item: the data to create contact
        :type contact_item: ContactCreate
        :param user_email: users email
        :type user_email: str
        :return: created Contact
        :rtype: ContactModel
        """
        new_contact = ContactModel(user_email=user_email, **contact_item.dict())
        self.db.add(new_contact)
        self.db.commit()
        self.db.refresh(new_contact)
        return new_contact

    async def get_by_id(self, id, user_email):
        """
        Retrieves a single contact with specified id for a specific user

        :param id: contacts id to retrieve
        :type id: int
        :param user_email: users email
        :type user_email: str
        :return: The contact with the specified ID, or None if it does not exist.
        :rtype: ContactModel | None
        """
        return self.db.query(ContactModel).filter(ContactModel.id == id, ContactModel.user_email == user_email).first()

    async def update(self, contact_item, id, user_email):
        """
        Update an existing contact with specified id for a specific user

        :param contact_item: the data to update in contacts info
        :type contact_item: ContactUpdate
        :param id: contacts id
        :type id: int
        :param user_email: users email
        :type user_email: str
        :return: updated contact or None if it does not exist
        :rtype: ContactModel | None
        """
        contact_for_update = self.db.query(ContactModel).filter(ContactModel.id == id,
                                                                ContactModel.user_email == user_email).first()
        if contact_for_update:
            contact_item_data = contact_item.dict(exclude_unset=True)
            for key, value in contact_item_data.items():
                setattr(contact_for_update, key, value)
            self.db.commit()
            return contact_for_update

    async def remove(self, id, user_email):
        """
        Delete a contact with specified id for a specific user

        :param id: contacts id
        :type id: int
        :param user_email: users email
        :type user_email: str
        :return: deleted contact or None if it does not exist
        :rtype: ContactModel | None
        """
        contact_to_delete = self.db.query(ContactModel).filter(ContactModel.id == id,
                                                               ContactModel.user_email == user_email).first()
        if contact_to_delete:
            self.db.delete(contact_to_delete)
            self.db.commit()
        return contact_to_delete

    async def get_by_first_name(self, first_name, user_email):
        """
        Retrieve a contact by first name for a specific user

        :param first_name: contacts first name
        :type first_name: str
        :param user_email: users email
        :type user_email: str
        :return: a contact with specified first name or None if it does not exist
        :rtype: ContactModel | None
        """
        return self.db.query(ContactModel).filter(ContactModel.first_name == first_name,
                                                  ContactModel.user_email == user_email).first()

    async def get_by_last_name(self, last_name, user_email):
        """
        Retrieve a contact by last name for a specific user

        :param last_name: contacts last name
        :type last_name: str
        :param user_email: users email
        :type user_email: str
        :return: a contact with specified last name or None if it does not exist
        :rtype: ContactModel | None
        """
        return self.db.query(ContactModel).filter(ContactModel.last_name == last_name,
                                                  ContactModel.user_email == user_email).first()

    async def get_by_email(self, email, user_email):
        """
        Retrieve a contact by email for a specific user

        :param email: contacts email
        :type email: str
        :param user_email: users email
        :type user_email: str
        :return: a contact with specified email or None if it does not exist
        :rtype: ContactModel | None
        """
        return self.db.query(ContactModel).filter(ContactModel.email == email,
                                                  ContactModel.user_email == user_email).first()

    async def contacts_birthdays_in_7_days(self, user_email):
        """
        Retrieves a contacts with birthday in next seven days

        :param user_email: users email
        :type user_email: str
        :return: list of contacts with birthday in next seven days
        :rtype: List[ContactModel]
        """
        end_date = date.today() + timedelta(days=7)

        return self.db.query(ContactModel).filter(ContactModel.user_email == user_email,
                                                  (ContactModel.birthday >= date.today()) &
                                                  (ContactModel.birthday <= end_date)
                                                  ).all()

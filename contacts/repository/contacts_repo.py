from datetime import date, timedelta

from models.contacts_model import ContactModel


class ContactsRepo():
    def __init__(self, db):
        self.db = db

    async def get_all(self, user_email):
        return self.db.query(ContactModel).filter(ContactModel.user_email == user_email).all()

    async def create(self, contact_item, user_email):
        new_contact = ContactModel(user_email=user_email, **contact_item.dict())
        self.db.add(new_contact)
        self.db.commit()
        self.db.refresh(new_contact)
        return new_contact

    async def get_by_id(self, id, user_email):
        return self.db.query(ContactModel).filter(ContactModel.id == id, ContactModel.user_email == user_email).first()

    async def update(self, contact_item, id, user_email):
        contact_for_update = (self.db.query(ContactModel).filter(ContactModel.id == id),
                              ContactModel.user_email == user_email.first())
        if contact_for_update:
            contact_item_data = contact_item.dict(exclude_unset=True)
            for key, value in contact_item_data.items():
                setattr(contact_for_update, key, value)
            self.db.commit()
            return contact_for_update

    async def remove(self, id, user_email):
        contact_to_delete = self.db.query(ContactModel).filter(ContactModel.id == id,
                                                               ContactModel.user_email == user_email).first()
        if contact_to_delete:
            self.db.delete(contact_to_delete)
            self.db.commit()
        return contact_to_delete

    async def get_by_first_name(self, first_name, user_email):
        return self.db.query(ContactModel).filter(ContactModel.first_name == first_name,
                                                  ContactModel.user_email == user_email).first()

    async def get_by_last_name(self, last_name, user_email):
        return self.db.query(ContactModel).filter(ContactModel.last_name == last_name,
                                                  ContactModel.user_email == user_email).first()

    async def get_by_email(self, email, user_email):
        return self.db.query(ContactModel).filter(ContactModel.email == email,
                                                  ContactModel.user_email == user_email).first()

    async def contacts_birthdays_in_7_days(self, user_email):
        end_date = date.today() + timedelta(days=7)

        return self.db.query(ContactModel).filter(ContactModel.user_email == user_email,
            (ContactModel.birthday >= date.today()) &
            (ContactModel.birthday <= end_date)
        ).all()

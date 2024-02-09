import unittest
from unittest.mock import MagicMock
from datetime import date, timedelta

from sqlalchemy.orm import Session

from contacts.models.contacts_model import ContactModel
from contacts.repository.contacts_repo import ContactsRepo
from contacts.schemas.contacts_schemas import ContactCreate, ContactUpdate


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.contacts_repo = ContactsRepo(self.session)
        self.user_email = "test@example.com"

    async def test_get_all_contacts(self):
        mock_contacts = [
            ContactModel(),
            ContactModel()
        ]
        self.session.query().filter().all.return_value = mock_contacts

        contacts = await self.contacts_repo.get_all(self.user_email)
        self.assertEqual(contacts, mock_contacts)

    async def test_create_contact(self):
        contact_data = ContactCreate(first_name="John", last_name="Doe", phone_number="123456789")
        created_contact = await self.contacts_repo.create(contact_data, self.user_email)

        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None

        self.assertEqual(created_contact.user_email, self.user_email)
        self.assertEqual(created_contact.first_name, "John")
        self.assertEqual(created_contact.phone_number, "123456789")

    async def test_get_contact_by_id_found(self):
        contact = ContactModel
        self.session.query().filter().first.return_value = contact

        result = await self.contacts_repo.get_by_id(id=1, user_email=self.user_email)

        self.assertEqual(result, contact)

    async def test_get_contact_by_id_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await self.contacts_repo.get_by_id(id=1, user_email=self.user_email)

        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        contact = ContactModel
        self.session.query().filter().first.return_value = contact

        result = await self.contacts_repo.remove(id=1, user_email=self.user_email)

        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await self.contacts_repo.remove(id=1, user_email=self.user_email)

        self.assertIsNone(result)

    async def test_update_contact_found(self):
        contact_item = ContactUpdate(first_name='Test', last_name='Tessssst', email=None,
                                     phone_number=None, birthday=None, favorite=True)
        contact = ContactModel
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None

        result = await self.contacts_repo.update(contact_item, id=1, user_email=self.user_email)

        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        contact_item = ContactUpdate(first_name='Test', last_name='Tessssst', email=None,
                                     phone_number=None, birthday=None, favorite=True)
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None

        result = await self.contacts_repo.update(contact_item, id=1, user_email=self.user_email)

        self.assertIsNone(result)

    async def test_get_by_first_name_found(self):
        first_name = "John"
        contact = ContactModel(first_name=first_name, last_name="Doe", phone_number="123456789")
        self.session.query().filter().first.return_value = contact

        result = await self.contacts_repo.get_by_first_name(first_name=first_name, user_email=self.user_email)

        self.assertEqual(result, contact)

    async def test_get_by_first_name_not_found(self):
        first_name = "John"
        self.session.query().filter().first.return_value = None

        result = await self.contacts_repo.get_by_first_name(first_name=first_name, user_email=self.user_email)

        self.assertIsNone(result)

    async def test_get_by_last_name_found(self):
        last_name = "Doe"
        contact = ContactModel(first_name="John", last_name=last_name, phone_number="123456789")
        self.session.query().filter().first.return_value = contact

        result = await self.contacts_repo.get_by_last_name(last_name=last_name, user_email=self.user_email)

        self.assertEqual(result, contact)

    async def test_get_by_last_name_not_found(self):
        last_name = "Doe"
        self.session.query().filter().first.return_value = None

        result = await self.contacts_repo.get_by_last_name(last_name=last_name, user_email=self.user_email)

        self.assertIsNone(result)

    async def test_get_by_email_found(self):
        email = "test@gmail.com"
        contact = ContactModel(first_name="John", last_name="Doe", phone_number="123456789", email=email)
        self.session.query().filter().first.return_value = contact

        result = await self.contacts_repo.get_by_email(email=email, user_email=self.user_email)

        self.assertEqual(result, contact)

    async def test_get_by_email_not_found(self):
        email = "test@gmail.com"
        self.session.query().filter().first.return_value = None

        result = await self.contacts_repo.get_by_email(email=email, user_email=self.user_email)

        self.assertIsNone(result)

    async def test_birthday_in_7_days_found(self):
        today = date.today()

        contacts = [ContactModel(first_name="John", last_name="Doe", phone_number="123456789",
                                 birthday=today + timedelta(days=3)), ContactModel(first_name="John", last_name="Doe",
                                                                                   phone_number="123456789",
                                                                                   birthday=today + timedelta(days=2)),
                    ContactModel(first_name="John", last_name="Doe",
                                 phone_number="123456789",
                                 birthday=today + timedelta(days=4))]

        self.session.query().filter().all.return_value = contacts
        result = await self.contacts_repo.contacts_birthdays_in_7_days(user_email=self.user_email)

        self.assertEqual(result, contacts)

    async def test_birthday_in_7_days_not_found(self):
        self.session.query().filter().all.return_value = None
        result = await self.contacts_repo.contacts_birthdays_in_7_days(user_email=self.user_email)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

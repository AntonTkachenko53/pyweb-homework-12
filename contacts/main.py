from fastapi import FastAPI
from api.contacts_items import router as contacts_router
from api.users_items import router as user_router
from models import contacts_model
from dependencies.database import engine

contacts_model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(contacts_router, prefix='/contacts')
app.include_router(user_router, prefix="/users")


@app.get('/')
async def health_check():
    print('or')
    return {'status': 'OK'}

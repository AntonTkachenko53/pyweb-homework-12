import cloudinary
import cloudinary.uploader as uploader
from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
  cloud_name=os.getenv("CLOUD_NAME"),
  api_key=os.getenv("API_KEY"),
  api_secret=os.getenv("API_SECRET")
)


def get_uploader():
    return uploader

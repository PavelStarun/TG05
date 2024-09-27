import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config import TOKEN, THE_CAT_API_KEY

# Вставьте сюда ваш токен телеграм-бота и API-ключ для TheCatAPI

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция для получения списка пород кошек
def get_cat_breeds():
   url = "https://api.thecatapi.com/v1/breeds"
   headers = {"x-api-key": THE_CAT_API_KEY}
   response = requests.get(url, headers=headers)
   return response.json()

# Функция для получения картинки кошки по породе
def get_cat_image_by_breed(breed_id):
   url = f"https://api.thecatapi.com/v1/images/search?breed_ids={breed_id}"
   headers = {"x-api-key": THE_CAT_API_KEY}
   response = requests.get(url, headers=headers)
   data = response.json()
   return data[0]['url']

# Функция для получения информации о породе кошек
def get_breed_info(breed_name):
   breeds = get_cat_breeds()
   for breed in breeds:
       if breed['name'].lower() == breed_name.lower():
           return breed
   return None

@dp.message(Command("start"))
async def start_command(message: Message):
   await message.answer("Привет! Напиши мне название породы кошки, и я пришлю тебе её фото и описание.")

@dp.message()
async def send_cat_info(message: Message):
   breed_name = message.text
   breed_info = get_breed_info(breed_name)
   if breed_info:
       cat_image_url = get_cat_image_by_breed(breed_info['id'])
       info = (
           f"Breed: {breed_info['name']}\n"
           f"Origin: {breed_info['origin']}\n"
           f"Description: {breed_info['description']}\n"
           f"Temperament: {breed_info['temperament']}\n"
           f"Life Span: {breed_info['life_span']} years"
       )
       await message.answer_photo(photo=cat_image_url, caption=info)
   else:
       await message.answer("Порода не найдена. Попробуйте еще раз.")

async def main():
   await dp.start_polling(bot)

if __name__ == '__main__':
   asyncio.run(main())

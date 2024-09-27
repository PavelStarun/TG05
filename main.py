import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import TOKEN, YOUTUBE_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик команды /start
async def send_welcome(message: Message):
    await message.answer("Привет! Я бот для поиска музыкального видео и(или) информации о канале на платформе YouTube.")

# Обработчик команды /help
async def send_help(message: Message):
    await message.answer("Используйте команды /find_song для поиска музыкального видео по исполнителю и /find_channel для получения информации о канале YouTube. Например, /find_song Linkin Park. Или /find_channel А4.")

# Обработчик команды /find_song
@dp.message(Command(commands=["find_song"]))
async def find_song_by_artist(message: Message):
    artist_name = message.text.replace("/find_song", "").strip()
    if not artist_name:
        await message.answer("Введите название исполнителя после /find_song для поиска музыкального видео. Например, /find_song Linkin Park.")
    else:
        await handle_song_request(message, artist_name)

# Обработчик команды /find_channel
@dp.message(Command(commands=["find_channel"]))
async def find_channel_info(message: Message):
    channel_name = message.text.replace("/find_channel", "").strip()
    if not channel_name:
        await message.answer("Введите название канала после /find_channel для получения информации. Например, /find_channel А4.")
    else:
        await handle_channel_request(message, channel_name)

# Функция для поиска музыкального видео через YouTube API
async def search_video_by_artist(artist_name: str):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": artist_name,
        "type": "video",
        "videoCategoryId": "10",  # Ищем только в категории музыки
        "key": YOUTUBE_API_KEY,
        "maxResults": 1
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = data.get("items", [])
                    if videos:
                        return videos[0]  # Возвращаем первое видео
                    else:
                        return None
                else:
                    print(f"Ошибка API: {response.status}")
                    return None
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

# Функция для поиска самого популярного видео канала
async def get_most_popular_video(channel_id: str):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "viewCount",  # Сортировка по количеству просмотров
        "maxResults": 1,
        "key": YOUTUBE_API_KEY,
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = data.get("items", [])
                    if videos:
                        video = videos[0]
                        return {
                            "title": video["snippet"]["title"],
                            "url": f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                        }
                    else:
                        return None
                else:
                    print(f"Ошибка API: {response.status}")
                    return None
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

# Функция для получения информации о канале YouTube
async def get_channel_info(channel_name: str):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": channel_name,
        "type": "channel",
        "key": YOUTUBE_API_KEY,
        "maxResults": 1
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    channels = data.get("items", [])
                    if channels:
                        channel_id = channels[0]["id"]["channelId"]
                        return await get_channel_statistics(channel_id)
                    else:
                        return None
                else:
                    print(f"Ошибка API: {response.status}")
                    return None
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

# Функция для получения статистики канала
async def get_channel_statistics(channel_id: str):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "statistics,snippet",
        "id": channel_id,
        "key": YOUTUBE_API_KEY,
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    channels = data.get("items", [])
                    if channels:
                        channel_info = channels[0]
                        stats = channel_info["statistics"]
                        most_popular_video = await get_most_popular_video(channel_info["id"])
                        return {
                            "title": channel_info["snippet"]["title"],
                            "video_count": stats["videoCount"],
                            "view_count": stats["viewCount"],
                            "most_popular_video": most_popular_video
                        }
                    else:
                        return None
                else:
                    print(f"Ошибка API: {response.status}")
                    return None
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

# Функция для обработки сообщений после команды /find_song
async def handle_song_request(message: Message, artist_name: str):
    video = await search_video_by_artist(artist_name)

    if video:
        video_id = video["id"]["videoId"]
        video_title = video["snippet"]["title"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        await message.answer(f"🎵 Найдено видео для {artist_name}:\n\n{video_title}\n\n▶️ Слушать: {video_url}")
    else:
        await message.answer(f"Не удалось найти видео для {artist_name}. Попробуйте позже.")

# Функция для обработки сообщений после команды /find_channel
async def handle_channel_request(message: Message, channel_name: str):
    channel_info = await get_channel_info(channel_name)

    if channel_info:
        await message.answer(
            f"📺 Канал: {channel_info['title']}\n"
            f"🎥 Загружено видео: {channel_info['video_count']}\n"
            f"👁️ Общие просмотры: {channel_info['view_count']}\n"
            f"🔥 Самое популярное видео: {channel_info['most_popular_video']['title']}\n"
            f"▶️ Ссылка: {channel_info['most_popular_video']['url']}"
        )
    else:
        await message.answer(f"Не удалось найти информацию о канале {channel_name}. Попробуйте позже.")

# Основная функция запуска бота
async def main():
    dp.message.register(send_welcome, Command(commands=["start"]))
    dp.message.register(send_help, Command(commands=["help"]))
    dp.message.register(find_song_by_artist, Command(commands=["find_song"]))
    dp.message.register(find_channel_info, Command(commands=["find_channel"]))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

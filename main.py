import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, MessageEntity

TOKEN = "9209616282:AAGsRLZuk1uViJgdXbw2mpEvsW0aX4553RY"

bot = Bot(TOKEN)
dp = Dispatcher()

EMOJIS = [
    ("😻", "6070890282386198374"),
    ("😶", "6070971684901359565"),
    ("🌝", "6069134439626051558"),
]

@dp.message(CommandStart())
async def start(message: Message):
    text = ""
    entities = []

    for emoji, emoji_id in EMOJIS:
        if emoji_id.startswith("YOUR_"):
            continue

        offset = len(text.encode("utf-16-le")) // 2
        length = len(emoji.encode("utf-16-le")) // 2

        text += emoji + " "

        entities.append(
            MessageEntity(
                type="custom_emoji",
                offset=offset,
                length=length,
                custom_emoji_id=emoji_id
            )
        )

    if entities:
        await message.answer(text, entities=entities)
    else:
        await message.answer("Add valid Custom Emoji IDs first!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

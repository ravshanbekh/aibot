import asyncio, logging, sys, os
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message,BotCommand
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api = "sk-il8U3j-Bk5siRro15gJPikS2ZP3GmRkOsrCbqxMXvuqnv7Hj2joQQSzjtboXStyjAE1tWZUDBaRITnI2aOnPpA"

client = OpenAI(
    base_url="https://api.langdock.com/openai/eu/v1",
    api_key=api
)

TOKEN = "7722450945:AAHsyQe_f3rJyePWUCBjGPx-9pmVTenm0l4"
dp = Dispatcher()

user_histories = {}

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="reset", description="Suhbatni yangilash"),
    ]
    await bot.set_my_commands(commands)

@dp.message(Command(commands="start"))
async def start(message: Message) -> None:
    await message.chat.do("typing")
    user_histories[message.from_user.id] = []
    await message.answer(f"Salom, {html.bold(message.from_user.full_name)}! \nRasm va matn yuborishingiz mumkin.")

@dp.message(Command(commands="help"))
async def help_command(message: Message):
    await message.answer("Bot matn va rasm qabul qiladi. /reset bosib suhbatni yangidan boshlang.")

@dp.message(Command(commands="reset"))
async def reset_command(message: Message):
    user_histories[message.from_user.id] = []
    await message.answer("Suhbat yangilandi. Yangi savollaringizni kutaman!")


@dp.message()
async def echo(message: Message) -> None:
    await message.chat.do("typing")
    user_id = message.from_user.id
    if user_id not in user_histories:
        user_histories[user_id] = []

    # Tekshir: rasm bormi
    if message.photo:
        file_id = message.photo[-1].file_id  # eng katta o'lchamdagi rasm
        bot = Bot(token=TOKEN)
        file_info = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        # Tarixga rasmni qo'shamiz
        user_histories[user_id].append({
            "role": "user",
            "content": [
                {"type": "text", "text": "Rasm yuborildi"},
                {"type": "image_url", "image_url": {"url": file_url}}
            ]
        })
    else:
        # Matn bo'lsa, oddiy matn qo'shamiz
        user_histories[user_id].append({"role": "user", "content": message.text})

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=user_histories[user_id]
        )

        reply = completion.choices[0].message.content

        user_histories[user_id].append({"role": "assistant", "content": reply})
        await message.answer(reply, parse_mode="Markdown")
    except Exception as e:
        await message.answer("Uzr, hozircha javob bera olmadim. Qayta urinib ko‘ring ")
        logging.error(f"Xatolik: {str(e)}")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

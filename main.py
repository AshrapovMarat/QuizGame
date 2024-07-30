import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F
from Config import API_TOKEN
from Data import quiz_data
from DB import get_quiz_index, update_quiz_index, create_table, get_count_correct_answers, get_count_incorrect_answers
from Quiz_manager import get_question, new_quiz

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

dp = Dispatcher()


# region Handlers
@dp.callback_query(F.data.startswith("right_answer:"))
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    _, answer_text = callback.data.split(':')
    await callback.message.answer(f"Верно! Ваш ответ: {answer_text}")
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index, 1, 0)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        count_correct_answers = await get_count_correct_answers(callback.from_user.id)
        count_incorrect_answers = await get_count_incorrect_answers(callback.from_user.id)
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! "
                                      f"У вас {count_correct_answers} правильных ответов "
                                      f"и {count_incorrect_answers} не правильных ответов.")


@dp.callback_query(F.data.startswith("wrong_answer:"))
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    _, answer_text = callback.data.split(':')
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"Неправильно. Ваш ответ: {answer_text}.\nПравильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index, 0, 1)
    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        count_correct_answers = await get_count_correct_answers(callback.from_user.id)
        count_incorrect_answers = await get_count_incorrect_answers(callback.from_user.id)
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! "
                                      f"У вас {count_correct_answers} правильных ответов "
                                      f"и {count_incorrect_answers} не правильных ответов.")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)
#endregion


async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
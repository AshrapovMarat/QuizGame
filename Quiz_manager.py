from Data import quiz_data
from aiogram.utils.keyboard import InlineKeyboardBuilder
from DB import get_quiz_index, reset_quiz
from aiogram import types

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"right_answer:{option}" if option == right_answer else f"wrong_answer:{option}")
        )
    builder.adjust(1)
    return builder.as_markup()

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    await reset_quiz(user_id)
    await get_question(message, user_id)
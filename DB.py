import aiosqlite
from Config import DB_NAME

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_quiz_index(user_id, index, correct_answer, incorrect_answer):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO quiz_state (user_id, question_index, correct_answers, incorrect_answers)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                question_index = excluded.question_index,
                correct_answers = quiz_state.correct_answers + excluded.correct_answers,
                incorrect_answers = quiz_state.incorrect_answers + excluded.incorrect_answers
        ''', (user_id, index, correct_answer, incorrect_answer))
        await db.commit()

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, 
        correct_answers INTEGER, incorrect_answers INTEGER)''')
        await db.commit()

async def reset_quiz(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, correct_answers, incorrect_answers) VALUES (?, 0, 0, 0)', (user_id,))
        await db.commit()

async def get_count_correct_answers(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT correct_answers FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def get_count_incorrect_answers(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT incorrect_answers FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
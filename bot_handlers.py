from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from quiz_data import quiz_data
from database import save_result, get_statistics
import random

class QuizStates(StatesGroup):
    answering = State()

async def start_command(message: types.Message):
    await message.answer("Привет, серфер! 🏄‍♂️ Готов проверить свои знания о кофе? Нажми /quiz, чтобы начать увлекательное путешествие в мир кофе!")

async def quiz_command(message: types.Message, state: FSMContext):
    await state.update_data(question_index=0, correct_answers=0, questions=random.sample(quiz_data, 10))
    await ask_question(message, state)
    await QuizStates.answering.set()

async def ask_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question_index = data['question_index']
    questions = data['questions']
    
    if question_index < len(questions):
        question = questions[question_index]['question']
        options = questions[question_index]['options']
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for option in options:
            keyboard.add(option)
        
        await message.answer(f"Вопрос {question_index + 1} из 10:\n\n{question}", reply_markup=keyboard)
    else:
        await finish_quiz(message, state)

async def process_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question_index = data['question_index']
    correct_answers = data['correct_answers']
    questions = data['questions']
    
    current_question = questions[question_index]
    if message.text == current_question['correct_option']:
        correct_answers += 1
        await message.answer("Отлично, друг! 🎉 Ты абсолютно прав!")
    else:
        await message.answer(f"Упс! Не совсем так, серфер. 😅 Правильный ответ: {current_question['correct_option']}")
    
    await message.answer(f"Твой ответ: {message.text}", reply_markup=types.ReplyKeyboardRemove())
    
    await state.update_data(question_index=question_index + 1, correct_answers=correct_answers)
    await ask_question(message, state)

async def finish_quiz(message: types.Message, state: FSMContext):
    data = await state.get_data()
    correct_answers = data['correct_answers']
    total_questions = 10
    
    result = f"Квиз завершен, серфер! 🏁\n\nТвой результат: {correct_answers} из {total_questions}"
    
    if correct_answers == total_questions:
        result += "\n\nВау! Ты настоящий кофейный гуру! ☕️👑"
    elif correct_answers >= 7:
        result += "\n\nОтличный результат! Ты точно любишь кофе! ☕️❤️"
    elif correct_answers >= 5:
        result += "\n\nНеплохо! Но ты можешь узнать о кофе еще больше! 📚☕️"
    else:
        result += "\n\nПохоже, тебе нужно выпить еще чашечку и подучить теорию! ☕️📖"

    await message.answer(result, reply_markup=types.ReplyKeyboardRemove())
    
    await save_result(message.from_user.id, correct_answers)
    await state.finish()

async def stats_command(message: types.Message):
    stats = await get_statistics()
    await message.answer(f"Статистика игроков, серфер! 📊\n\n{stats}")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(quiz_command, commands=['quiz'])
    dp.register_message_handler(stats_command, commands=['stats'])
    dp.register_message_handler(process_answer, state=QuizStates.answering)
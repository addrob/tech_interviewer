import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from src.bot.keyboards import QuestionCallbackFactory, StartCommandKeyboard, AnswerCallbackFactory, \
    TopicCallbackFactory, \
    SubTopicCallbackFactory
from src.bot.config import TG_API_KEY, MY_CHAT_ID
from src.db.models import Topic, SubTopic, Question, Answer


bot = Bot(token=TG_API_KEY)
dp = Dispatcher()


class AddContent(StatesGroup):
    """
    FSM состояний добавления вопроса
    """
    add_topic = State()  # добавление темы
    add_subtopic = State()  # добавление подтемы
    add_question = State()  # добавление вопроса
    add_answer = State()  # добавление ответа


class GetAnswer(StatesGroup):
    """
    FSM состояния получения ответа на вопрос
    """
    waiting_for_answer = State()  # ожидание ответа на вопрос


def get_random_question():
    """
    Функция возвращает случайный вопрос из базы данных
    """
    topic = Topic.get_random()
    subtopic = SubTopic.get_random_by_topic(topic)
    return Question.get_random_by_subtopic(subtopic)


@dp.message(Command("start"))
async def start(message: types.Message):
    """
    Обработчик команды /start.
    Отправляет приветственное сообщение и выводит клавиатуру с командами
    :param message: сообщение
    """
    await message.answer("Hello!", reply_markup=StartCommandKeyboard.get_keyboard())


@dp.message(Command('question'))
async def get_question(message: types.Message,
                       state: FSMContext):
    """
    Обработчик команды /question
    Отправляет случайный вопрос из базы данных, для вопроса выводит инлайн-клавиатуру с возможностью вывода ответа
    Сохраняет ответ на вопрос в состоянии пользователя
    :param message: сообщение
    :param state: состояние
    """
    question = get_random_question()
    await message.answer(text=question.text, reply_markup=QuestionCallbackFactory.get_keyboard())
    await state.set_state(GetAnswer.waiting_for_answer)
    await state.update_data(answer=question.answer[0].text)


@dp.callback_query(QuestionCallbackFactory.filter(), GetAnswer.waiting_for_answer)
async def question_callback_handler(callback: types.CallbackQuery,
                                    state: FSMContext,
                                    callback_data: QuestionCallbackFactory):
    """
    Обработчик коллбэка при нажатии на кнопку "Показать ответ" у сообщения, полученного из /question
    Возвращает ответ на вопрос из состояния пользователя
    :param callback: коллбэк
    :param state: состояние
    :param callback_data: данные коллбэка
    """
    user_data = await state.get_data()
    if callback_data.action == 'answer':
        await callback.message.answer(text=user_data['answer'])
    await callback.answer()
    await state.clear()


@dp.callback_query(AnswerCallbackFactory.filter())
async def answer_callback_handler(callback: types.CallbackQuery,
                                  callback_data: AnswerCallbackFactory):
    """
    Обработчик коллбэка при нажатии на кнопку "Показать ответ" у сообщения, полученного из рассылки
    Возвращает из базы данных ответ на вопрос по его id, полученного из данных коллбэка
    :param callback: коллбэк
    :param callback_data: данные коллбэка
    """
    answer = Answer.get_by_id(callback_data.answer_id)
    await callback.message.answer(answer.text)
    await callback.answer()


@dp.message(Command('add'))
async def set_add_state(message: types.Message,
                        state: FSMContext):
    """
    Обработчик команды /add
    Переводит пользователя в состояние ожидания json с вопросом
    :param message: сообщение
    :param state: состояние
    """
    topics = Topic.get_topics()
    await message.answer(text='Передайте или выберите тему вопроса',
                         reply_markup=TopicCallbackFactory.get_keyboard(topics=topics))
    await state.set_state(AddContent.add_topic)


@dp.message(AddContent.add_topic)
async def add_topic(message: types.Message,
                    state: FSMContext):
    """
    Обработчик состояния ожидания json с вопросом
    Добавляет в базу данных переданный вопрос
    :param message: сообщение
    """
    topic = Topic.add_topic(message.text)
    subtopics = SubTopic.get_by_topic_id(topic.id)
    await message.answer(text='Передайте или выберите подтему вопроса',
                         reply_markup=SubTopicCallbackFactory.get_keyboard(subtopics=subtopics))
    await state.set_state(AddContent.add_subtopic)
    await state.update_data(topic_id=topic.id)


@dp.message(AddContent.add_subtopic)
async def add_subtopic(message: types.Message,
                       state: FSMContext):
    """
    Обработчик состояния ожидания json с вопросом
    Добавляет в базу данных переданный вопрос
    :param message: сообщение
    """
    user_data = await state.get_data()
    subtopic = SubTopic.add_subtopic(name=message.text,
                                     topic_id=user_data['topic_id'])
    await message.answer(text='Передайте вопрос')
    await state.set_state(AddContent.add_question)
    await state.update_data(subtopic_id=subtopic.id)


@dp.message(AddContent.add_question)
async def add_question(message: types.Message,
                       state: FSMContext):
    """
    Обработчик состояния ожидания json с вопросом
    Добавляет в базу данных переданный вопрос
    :param message: сообщение
    """
    user_data = await state.get_data()
    question = Question.add_question(text=message.text,
                                     subtopic_id=user_data['subtopic_id'])
    await message.answer(text='Передайте ответ')
    await state.set_state(AddContent.add_answer)
    await state.update_data(question_id=question.id)


@dp.message(AddContent.add_answer)
async def add_answer(message: types.Message,
                     state: FSMContext):
    """
    Обработчик состояния ожидания json с вопросом
    Добавляет в базу данных переданный вопрос
    :param message: сообщение
    """
    user_data = await state.get_data()
    question = Question.get_by_id(user_data['question_id'])
    answer = Answer.add_answer(text=message.text,
                               question=question)
    await message.answer(text='Вопрос сохранен')
    await state.clear()


@dp.callback_query(TopicCallbackFactory.filter())
async def add_topic_callback_handler(callback: types.CallbackQuery,
                                     callback_data: TopicCallbackFactory,
                                     state: FSMContext):
    """
    Обработчик коллбэков при нажатии кнопки Добавить тему
    :param callback: коллбэк
    :param callback_data: данные коллбэка
    :param state: состояние
    """
    subtopics = SubTopic.get_by_topic_id(topic_id=callback_data.topic_id)
    await callback.message.answer(text='Передайте или выберите подтему',
                                  reply_markup=SubTopicCallbackFactory.get_keyboard(subtopics=subtopics))
    await callback.answer()
    await state.set_state(AddContent.add_subtopic)
    await state.update_data(topic_id=callback_data.topic_id)


@dp.callback_query(SubTopicCallbackFactory.filter())
async def add_subtopic_callback_handler(callback: types.CallbackQuery,
                                        callback_data: SubTopicCallbackFactory,
                                        state: FSMContext):
    """
    Обработчик колллбэков при нажатии кнопки Добавить подтему
    :param callback: коллбэк
    :param callback_data: данные коллбэка
    :param state: состояние
    """
    await callback.message.answer(text='Передайте вопрос')
    await state.set_state(AddContent.add_question)
    await state.update_data(subtopic_id=callback_data.subtopic_id)
    await callback.answer()


async def send_message():
    """
    Отправка сообщения со случаный вопросом
    """
    question = get_random_question()
    await bot.send_message(chat_id=MY_CHAT_ID,
                           text=question.text,
                           reply_markup=AnswerCallbackFactory.get_keyboard(question))


async def scheduler(job=send_message,
                    time_to: int = 21,
                    time_from: int = 11,
                    interval: str = '0, 30'):
    """
    Планировщик выполнения события
    :param job: событие
    :param time_to: верхняя граница времени суток
    :param time_from: нижняя граница времени суток
    :param interval: интервал выполнения
    """
    timezone = pytz.timezone('Europe/Moscow')
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job,
                      trigger='cron',
                      minute=interval,
                      hour=f'{time_from}-{time_to}',
                      timezone=timezone)
    scheduler.start()


async def main():
    """
    Запуск бота
    """
    dp.startup.register(scheduler)
    await dp.start_polling(bot)


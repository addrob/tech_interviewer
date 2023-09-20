from typing import Optional
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


class QuestionCallbackFactory(CallbackData, prefix='question'):
    action: str

    @classmethod
    def get_keyboard(cls):
        builder = InlineKeyboardBuilder()
        builder.button(
            text='Показать ответ',
            callback_data=cls(action='answer')
        )
        return builder.as_markup()


class StartCommandKeyboard:
    @classmethod
    def get_keyboard(cls):
        buttons = [[types.KeyboardButton(text='/question'),
                    types.KeyboardButton(text='/add')]]
        keyboard = types.ReplyKeyboardMarkup(keyboard=buttons,
                                             resize_keyboard=True)
        return keyboard


class AnswerCallbackFactory(CallbackData, prefix='answer'):
    answer_id: Optional[int]

    @classmethod
    def get_keyboard(cls, question):
        builder = InlineKeyboardBuilder()
        builder.button(
            text='Показать ответ',
            callback_data=cls(answer_id=question.answer[0].id)
        )
        return builder.as_markup()


class TopicCallbackFactory(CallbackData, prefix='topic'):
    topic_id: Optional[int]

    @classmethod
    def get_keyboard(cls, topics):
        builder = InlineKeyboardBuilder()
        for topic in topics:
            topic = topic[0]
            builder.button(
                text=topic.name,
                callback_data=cls(topic_id=topic.id)
            )
        return builder.as_markup()


class SubTopicCallbackFactory(CallbackData, prefix='subtopic'):
    subtopic_id: Optional[int]

    @classmethod
    def get_keyboard(cls, subtopics):
        builder = InlineKeyboardBuilder()
        for subtopic in subtopics:
            subtopic = subtopic[0]
            builder.button(
                text=subtopic.name,
                callback_data=cls(subtopic_id=subtopic.id)
            )
        return builder.as_markup()

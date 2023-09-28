import random

from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship

from src.db.config import Base, session


class Answer(Base):
    """
    Модель Ответов
    """
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    question = relationship('Question', uselist=False, back_populates='answer')
    question_id = Column(ForeignKey('questions.id'))

    @classmethod
    def add_answer(cls,
                   text: str,
                   question: 'Question'):
        """
        Добавить ответ
        :param text: текст ответа
        :param question: объект вопроса, к которому добавляется ответ
        """
        answer = cls(text=text,
                     question=question)
        session.add(answer)
        session.commit()
        return answer

    @classmethod
    def get_by_id(cls,
                  answer_id: int):
        """
        Получение ответа по id
        :param answer_id: id ответ
        """
        answer = session.execute(select(cls).where(cls.id == answer_id)).fetchone()[0]
        return answer


class Question(Base):
    """
    Модель вопроса
    """
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    answer = relationship('Answer', back_populates='question')
    subtopic = Column(Integer, ForeignKey('subtopics.id'))

    @classmethod
    def add_question(cls,
                     text: str,
                     subtopic_id: int):
        """
        Добавить ответ
        :param text: текст ответа
        :param subtopic_id: id подтемы
        """
        question = cls(text=text,
                       subtopic=subtopic_id)
        session.add(question)
        session.commit()
        return question

    @classmethod
    def get_random_by_subtopic(cls,
                               subtopic: 'SubTopic'):
        """
        Получение рандомного вопроса по переданной подтеме
        :param subtopic: подтема
        """
        questions = session.execute(select(cls).where(cls.subtopic == subtopic.id)).fetchall()
        question_id = random.choice(questions)[0].id
        return session.execute(select(cls).where(cls.id == question_id)).fetchone()[0]

    @classmethod
    def get_by_id(cls,
                  question_id: int):
        """
        Получение вопроса по id
        :param question_id: id вопроса
        """
        return session.execute(select(cls).where(cls.id == question_id)).fetchone()[0]

    def get_text_formatted(self):
        subtopic = SubTopic.get_by_id(self.subtopic)
        topic = Topic.get_by_id(subtopic.topic)
        text = f'{topic.name} -- {subtopic.name}: \n\n{self.text}'
        return text


class SubTopic(Base):
    """
    Модель подтемы
    """
    __tablename__ = 'subtopics'
    id = Column(Integer, primary_key=True)
    topic = Column(Integer, ForeignKey('topics.id'))
    name = Column(String)
    questions = relationship(Question)

    @classmethod
    def add_subtopic(cls,
                     name: str,
                     topic_id: int):
        """
        Добавить подтему
        :param name: название подтемы
        :param topic_id: id темы
        """
        existing_subtopics = session.execute(select(cls)).fetchall()
        for existing_subtopic in existing_subtopics:
            existing_subtopic = existing_subtopic[0]
            if name == existing_subtopic.name and topic_id == existing_subtopic.topic:
                return existing_subtopic
        subtopic = cls(name=name, topic=topic_id)
        session.add(subtopic)
        session.commit()
        return subtopic

    @classmethod
    def get_random_by_topic(cls,
                            topic: 'Topic'):
        """
        Получение рандомной подтемы по переданной теме
        :param topic: тема
        """
        subtopics = session.execute(select(cls).where(cls.topic == topic.id)).fetchall()
        subtopic_id = random.choice(subtopics)[0].id
        return session.execute(select(cls).where(cls.id == subtopic_id)).fetchone()[0]

    @classmethod
    def get_by_id(cls, subtopic_id: int):
        return session.execute(select(cls).where(cls.id == subtopic_id)).fetchone()[0]

    @classmethod
    def get_by_topic_id(cls, topic_id: int):
        """
        Получение подтем по id темы
        :param topic_id: id темы
        """
        return session.execute(select(cls).where(cls.topic == topic_id)).fetchall()


class Topic(Base):
    """
    Модель темы
    """
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    subtopics = relationship(SubTopic)
    name = Column(String)

    @classmethod
    def add_topic(cls,
                  name: str):
        """
        Добавление темы
        :param name: название темы
        """
        existing_topics = session.execute(select(cls)).fetchall()
        for existing_topic in existing_topics:
            existing_topic = existing_topic[0]
            if name == existing_topic.name:
                return existing_topic
        topic = cls(name=name)
        session.add(topic)
        session.commit()
        return topic

    @classmethod
    def get_random(cls):
        """
        Получение рандомной темы
        """
        topics = session.execute(select(cls)).fetchall()
        topic_id = random.choice(topics)[0].id
        return session.execute(select(cls).where(cls.id == topic_id)).fetchone()[0]

    @classmethod
    def get_topics(cls):
        """
        Получение всех тем
        """
        return session.execute(select(cls)).fetchall()

    @classmethod
    def get_by_id(cls, topic_id: int):
        return session.execute(select(cls).where(cls.id == topic_id)).fetchone()[0]



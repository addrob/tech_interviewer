import random
from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship

from src.db.config import Base, session


class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    question = relationship('Question', uselist=False, back_populates='answer')
    question_id = Column(ForeignKey('questions.id'))

    @classmethod
    def add_answer(cls,
                   text: str,
                   question: 'Question'):
        answer = cls(text=text,
                     question=question)
        session.add(answer)
        session.commit()
        return answer

    @classmethod
    def get_by_id(cls,
                  answer_id: int):
        answer = session.execute(select(cls).where(cls.id == answer_id)).one()[0]
        return answer


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    answer = relationship('Answer', back_populates='question')
    subtopic = Column(Integer, ForeignKey('subtopics.id'))

    @classmethod
    def add_question(cls,
                     text: str,
                     subtopic_id: int):
        question = cls(text=text,
                       subtopic=subtopic_id)
        session.add(question)
        session.commit()
        return question

    @classmethod
    def get_random_by_subtopic(cls,
                               subtopic: 'SubTopic'):
        questions = session.execute(select(cls).where(cls.subtopic == subtopic.id)).all()
        question_id = random.choice(questions)[0].id
        print('question_id ', question_id)
        return session.execute(select(cls).where(cls.id == question_id)).one()[0]

    @classmethod
    def get_by_id(cls,
                  question_id: int):
        return session.execute(select(cls).where(cls.id == question_id)).one()[0]


class SubTopic(Base):
    __tablename__ = 'subtopics'
    id = Column(Integer, primary_key=True)
    topic = Column(Integer, ForeignKey('topics.id'))
    name = Column(String)
    questions = relationship(Question)

    @classmethod
    def add_subtopic(cls,
                     name: str,
                     topic_id: int):
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
        subtopics = session.execute(select(cls).where(cls.topic == topic.id)).fetchall()
        subtopic_id = random.choice(subtopics)[0].id
        return session.execute(select(cls).where(cls.id == subtopic_id)).one()[0]

    @classmethod
    def get_by_topic_id(cls, topic_id: int):
        return session.execute(select(cls).where(cls.topic == topic_id)).fetchall()


class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    subtopics = relationship(SubTopic)
    name = Column(String)

    @classmethod
    def add_topic(cls,
                  name: str):
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
        topics = session.execute(select(cls)).all()
        topic_id = random.choice(topics)[0].id
        return session.execute(select(cls).where(cls.id == topic_id)).one()[0]

    @classmethod
    def get_topics(cls):
        return session.execute(select(cls)).all()



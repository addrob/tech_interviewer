from src.db.models import Topic, SubTopic, Question, Answer


def parse_json(json_obj: dict):
    topics = json_obj.keys()
    for topic_name in topics:
        topic = Topic.add_topic(name=topic_name)
        print(topic)
        subtopics = json_obj[topic_name]
        for subtopic in subtopics:
            print(subtopic['subtopic'])
            print(subtopic)
            subtopic_name = subtopic['subtopic']
            subtopic_obj = SubTopic.add_subtopic(name=subtopic_name, topic=topic)
            questions = subtopic['questions']
            for question in questions:
                answer = Answer(text=question['answer'])
                Question.add_question(text=question['question'], answer=answer, subtopic=subtopic_obj)





# parse_json({
#     "FastAPI": [
#         {
#             "subtopic": "Основы FastAPI",
#             "questions": [
#                 {
#                     "question": "Что такое FastAPI и для чего он используется?",
#                     "answer": "FastAPI — это современный, быстрый веб-фреймворк для создания API на Python 3.6+. Он основан на стандартах OpenAPI и JSON Schema и предназначен для создания RESTful API."
#                 },
#                 {
#                     "question": "Чем FastAPI отличается от Flask и Django?",
#                     "answer": "FastAPI предлагает автоматическую генерацию документации, использует Pydantic для валидации данных и встроенно поддерживает асинхронные запросы. Flask и Django не имеют этих возможностей из коробки и требуют дополнительных расширений."
#                 },
#             ]
#         }
#     ],
#     "SQLAlchemy": [
#         {
#             "subtopic": "Основы SQLAlchemy",
#             "questions": [
#                 {
#                     "question": "Что такое ORM и какую проблему он решает?",
#                     "answer": "ORM (Object-Relational Mapping) — это методология программирования, которая позволяет работать с базами данных как с обычными объектами Python. Она решает проблему сопоставления объектов в коде с записями в базе данных."
#                 }
#             ]
#         },
#     ]})

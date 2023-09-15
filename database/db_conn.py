from sqlalchemy import Integer, String, BOOLEAN, DateTime, Column, ForeignKeyConstraint, text
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.sql.functions import func
import json

Base = declarative_base()


class Category(Base):
    __tablename__ = "category"
    __table_args__ = {'extend_existing': True}

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    category_name = Column('category_name', String(100), unique=True, nullable=False)

    @staticmethod
    def save(engine, obj):
        session = Session(bind=engine)
        session.add(obj)
        session.commit()
        session.close()

    @staticmethod
    def get_categories(engine):
        session = Session(bind=engine)
        query = session.query(Category).all()
        categories = []
        for row in query:
            categories.append(row.category_name)
        session.close()
        return categories


class Animals(Base):
    __tablename__ = "animals"
    __table_args__ = {'extend_existing': True}

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(100), unique=True, nullable=False)
    description = Column('description', String, unique=True, nullable=False)
    scores = Column('scores', String, unique=False, nullable=False)
    link = Column('link', String, unique=False, nullable=False)

    @staticmethod
    def save(engine, obj):
        session = Session(bind=engine)
        session.add(obj)
        session.commit()
        session.close()

    @staticmethod
    def save_animals(engine, descriptions, scores, links):
        session = Session(bind=engine)
        objs = []
        for i in scores.keys():
            '''nsc = {}
            for key in scores[i]:
                nsc[key] = scores[i][key]-4'''
            objs.append(Animals(name=i, description=descriptions[i], scores=json.dumps(scores[i]), link=links[i]))
        session.add_all(objs)
        session.commit()
        session.close()

    @staticmethod
    def get_animals(engine):
        session = Session(bind=engine)
        descriptions, scores, links = {}, {}, {}
        query = session.query(Animals).all()
        for row in query:
            descriptions[row.name] = row.description
            scores[row.name] = json.loads(row.scores)
            links[row.name] = row.link
        session.close()
        return descriptions, scores, links

    @staticmethod
    def del_animals(engine):
        session = Session(bind=engine)
        session.query(Animals).delete()
        session.commit()
        session.close()


class Questions(Base):
    __tablename__ = "questions"
    __table_args__ = {'extend_existing': True}

    number = Column('number', Integer, primary_key=True, autoincrement=False)
    question = Column('question', String(255), unique=True, nullable=False)
    answers = Column('answers', String, unique=False, nullable=False)

    @staticmethod
    def save(engine, obj):
        session = Session(bind=engine)
        session.add(obj)
        session.commit()
        session.close()

    @staticmethod
    def get_questions(engine):
        session = Session(bind=engine)
        query = session.query(Questions).all()
        questions = []
        for row in query:
            questions.append([])
            questions[len(questions)-1].append(row.question)
            questions[len(questions)-1].append(json.loads(row.answers))

        session.close()
        return questions

    @staticmethod
    def save_questions(engine, questions):
        session = Session(bind=engine)
        objs = []
        i = 1
        for q in questions:
            objs.append(Questions(number=i, question=q[0], answers=json.dumps(q[1])))
            i += 1
        session.add_all(objs)
        session.commit()
        session.close()

    @staticmethod
    def del_questions(engine):
        session = Session(bind=engine)
        session.query(Questions).delete()
        session.commit()
        session.close()


class Sessions(Base):
    __tablename__ = "sessions"
    __table_args__ = {'extend_existing': True}

    user_id = Column("user_id", Integer, nullable=False, primary_key=True)
    cur_qst_num = Column("cur_qst_num", Integer, nullable=False, unique=False, default=0)
    at_welcome = Column("at_welcome", BOOLEAN, nullable=False, unique=False, default=False)
    is_comment = Column("is_comment", BOOLEAN, nullable=False, unique=False, default=False)

    @staticmethod
    def save(engine, obj):
        session = Session(bind=engine)
        session.add(obj)
        session.commit()
        session.close()

    @staticmethod
    def add_session(engine, user_id):
        session = Session(bind=engine)
        obj = Sessions(user_id=user_id)
        session.add(obj)
        session.commit()
        session.close()

    @staticmethod
    def get_session(engine, user_id):
        session = Session(bind=engine)
        obj = session.query(Sessions).filter(Sessions.user_id == user_id).first()
        session.close()
        return obj

    @staticmethod
    def del_session(engine, user_id):
        session = Session(bind=engine)
        session.query(Sessions).filter(Sessions.user_id == user_id).delete()
        session.commit()
        session.close()

    @staticmethod
    def check_session(engine, user_id):
        session = Session(bind=engine)
        flag = session.query(Sessions).filter(Sessions.user_id == user_id).first() is not None
        session.close()
        return flag

    @staticmethod
    def get_cur_question(engine, user_id):
        session = Session(bind=engine)
        cur_q = session.query(Sessions).filter(Sessions.user_id == user_id).first().cur_qst_num
        session.close()
        return cur_q

    @staticmethod
    def next_question(engine, user_id):
        session = Session(bind=engine)
        obj = session.query(Sessions).filter(Sessions.user_id == user_id).first()
        if obj is not None:
            obj.cur_qst_num += 1
            session.add(obj)
            session.commit()
        session.close()


class Scores(Base):
    __tablename__ = "scores"
    __table_args__ = (ForeignKeyConstraint(['user_id'], ['sessions.user_id']),
                      ForeignKeyConstraint(['category_name'], ['category.category_name']),
                      {'extend_existing': True})

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id = Column("user_id", Integer, nullable=False, unique=False)
    category_name = Column("category_name", String(100), nullable=False, unique=False)
    score = Column("score", Integer, nullable=False, unique=False, default=0)

    @staticmethod
    def save(engine, obj):
        session = Session(bind=engine)
        session.add(obj)
        session.commit()
        session.close()

    @staticmethod
    def add_scores(engine, user_id):
        session = Session(bind=engine)
        q = session.query(Category).all()
        for cat in q:
            obj = Scores(user_id=user_id, category_name=cat.category_name)
            session.add(obj)
        session.commit()
        session.close()

    @staticmethod
    def del_scores(engine, user_id):
        session = Session(bind=engine)
        session.query(Scores).filter(Scores.user_id == user_id).delete()
        session.commit()
        session.close()

    @staticmethod
    def update_scores(engine, user_id, category_name, score):
        session = Session(bind=engine)
        obj = session.query(Scores).filter(Scores.user_id == user_id, Scores.category_name == category_name).first()
        if obj is not None:
            obj.score += score
            session.add(obj)
            session.commit()
        session.close()

    @staticmethod
    def get_scores(engine, user_id):
        session = Session(bind=engine)
        query = session.query(Scores).filter(Scores.user_id == user_id)
        scores = {}
        for row in query:
            scores[row.category_name] = row.score
        session.close()
        return scores

    @staticmethod
    def get_scores_2(engine, user_id):
        with engine.connect() as conn:
            res = conn.execute(text("select score, category_name from scores where user_id=%s" % user_id))
            scores = {}
            for r in res:
                scores[r.category_name] = r.score
        return scores

    @staticmethod
    def get_text(engine, user_id):
        session = Session(bind=engine)
        objs = session.query(Scores).filter(Scores.user_id == user_id)
        text = ""
        for obj in objs:
            text += obj.category_name + ": " + str(obj.score) + "\n"
        session.close()
        return text


class Statistics(Base):
    __tablename__ = "statistics"
    __table_args__ = (ForeignKeyConstraint(['animal_name'], ['animals.name']),
                      {'extend_existing': True})

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    animal_name = Column("animal_name", String(100), nullable=False, unique=False)
    score = Column("score", Integer, nullable=False, unique=False, default=0)

    @staticmethod
    def update_score(engine, animal_name):
        session = Session(bind=engine)
        q = session.query(Statistics).filter(Statistics.animal_name == animal_name).first()
        if q is not None:
            q.score += 1
        else:
            q = Statistics(animal_name=animal_name, score=1)
        session.add(q)
        session.commit()
        session.close()


class Reviews(Base):
    __tablename__ = "reviews"
    __table_args__ = {'extend_existing': True}

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    review = Column("review", String, nullable=False, unique=False)
    creation_date = Column("creation_date", DateTime(timezone=True), nullable=False, server_default=func.now())

    @staticmethod
    def save(engine, obj):
        session = Session(bind=engine)
        session.add(obj)
        session.commit()
        session.close()


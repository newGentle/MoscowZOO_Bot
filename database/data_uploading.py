from db_conn import Category, Questions, Animals, Base
from data import categories, questions,  animals_link, animals_parameters, animals_description
from sqlalchemy import create_engine

eng = create_engine("sqlite:///database.db")
Base.metadata.create_all(eng)

for i in categories.keys():
    cat = Category(category_name=categories[i])
    Category.save(eng, cat)

Questions.save_questions(eng, questions)

Animals.save_animals(eng, animals_description, animals_parameters, animals_link)

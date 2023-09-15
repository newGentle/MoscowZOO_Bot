from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_conn import Questions
from sqlalchemy import create_engine
from database.data import message


# Меню после приветствие
bot_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
quiz_btn = KeyboardButton(text="Играть")
ticket_btn = KeyboardButton(text="Купить билеты")
site_btn = KeyboardButton(text="Узнать о круге друзей")
contacts_btn = KeyboardButton(text="Связаться с  нами")
review_btn = KeyboardButton(text="Оставить отзыв")
bot_menu.add(quiz_btn)
bot_menu.add(ticket_btn, site_btn)
bot_menu.add(contacts_btn, review_btn)

# -------------------------------------------------------------

# Меню начало Викторины
quiz_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
begin_btn = KeyboardButton("Начали")
cancel_btn = KeyboardButton("Отмена")
quiz_menu.insert(begin_btn)
quiz_menu.insert(cancel_btn)
# -------------------------------------------------------------

# Меню сброса Викторины или продолжения Викторины
quiz_menu_continue = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
continue_quiz_btn = KeyboardButton("Продолжить")
cancel_quiz_btn = KeyboardButton("Отмена")
reset_quiz_btn = KeyboardButton("Сбросить")
quiz_menu_continue.insert(continue_quiz_btn)
quiz_menu_continue.insert(cancel_quiz_btn)
quiz_menu_continue.add(reset_quiz_btn)
# -------------------------------------------------------------

quiz_stop = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
quiz_stop_button = KeyboardButton("Остановить игру")
quiz_stop.add(quiz_stop_button)

# -------------------------------------------------------------

review_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
review_cancel_btn = KeyboardButton("Отмена")
review_cancel.add(review_cancel_btn)


engine = create_engine("sqlite:///database\\database.db")

questions = Questions.get_questions(engine)


def quiz_buttons(cur_qst):
    # print(questions[ques_Num][1])
    quiz = InlineKeyboardMarkup(row_width=3)
    for key, value in questions[cur_qst][1].items():
        quiz.add(InlineKeyboardButton(text=value['name'], callback_data=key))
    return quiz


def final_message(scores:dict):
    msg = []
    for key in scores.keys():
        if -4 <= scores[key] <= -2:
            msg.append(message[key][0])
    for key in scores.keys():
        if -1 <= scores[key] <= 1:
            msg.append(message[key][1])
    for key in scores.keys():
        if 2 <= scores[key] <= 4:
            msg.append(message[key][2])
    s = ''.join(msg)
    return s


def choose(animal_scores, categories, our_scores):
    check = {}
    min_avg = float("inf")
    totems = []

    for i in animal_scores.keys():
        check[i] = {}
        check[i]["avg"] = 0
        for j in categories:
            scope = animal_scores[i][j]
            res = scope - our_scores[j]
            if res < 0:
                res *= -1
            check[i][j] = res
            check[i]['avg'] += res

        cur_checks = check[i]["avg"]
        if cur_checks < min_avg:
            min_avg = cur_checks
            totems = [i]
        elif cur_checks == min_avg:
            totems.append(i)

    return totems[0]
from aiogram import Bot, Dispatcher, executor, types

from mail.mail import send_mail

from extensions import quiz_buttons, quiz_menu_continue, quiz_menu, bot_menu, quiz_stop, review_cancel, final_message, choose
from database.db_conn import Category, Sessions, Scores, Questions, Animals, Statistics, Reviews
from sqlalchemy import create_engine
from aiogram.dispatcher.filters import Text

import os
from dotenv import load_dotenv

load_dotenv('creds.env')

bot = Bot(token=os.environ.get("API_TOKEN"))

dp = Dispatcher(bot=bot)

engine = create_engine("sqlite:///database\\database.db")

questions = Questions.get_questions(engine)
descriptions, scores, links = Animals.get_animals(engine)
categories = Category.get_categories(engine)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    photo = open('images/welcome-img1.png', mode='+rb')
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await bot.send_photo(photo=photo, chat_id=message.chat.id, caption='Чтобы наше общение было веселым и полезным вы можете вспомнить детство и сыграть в веселую викторину !\n'
            'Ответив на все вопросы вы сможете определить свое тотемное животное и узнать о себе немного больше !\n'
            'Для прохождения викторины нажмите Играть ! 👇\n\n'
            
            'Если вы соскучились по милым, забавным, немного опасным, но безумно интересным животным,'
            'то Вам срочно нужно сходить в Московский зоопарк!\n Для покупки билетов нажмите кнопку Купить билеты.\n\n'
            
            'А еще, если вы хотите помочь животным и поделится частичкой своей доброты,'
            'то можете присоединится к нашему Кругу Друзей и даже взять свой тотем или другое понравившееся животное под опеку.\n'
            'Если хотите узнать больше об этой программе нажмите Узнать о Круге друзей.\n\n'
            
            'Если у вас остались вопросы или вы хотите взять животное под опеку нажмите Связаться с нами.', 
            reply_markup=bot_menu
             )
                         

@dp.message_handler(Text("Играть"))
async def begin_quiz(message: types.Message):
    user_id = message.from_user.id

    if Sessions.check_session(engine, user_id):
        sess = Sessions.get_session(engine, user_id)
        sess.at_welcome = True
        Sessions.save(engine, sess)
        await message.answer('Вы уже начинали проходить викторину.', reply_markup=quiz_menu_continue)
    else:
        await bot.send_message(text='Помните в детстве были анкеты и тесты, которые мы передавали друг другу?\n'
                                    'Хотите вспомнить как это было?\n Тогда получайте вопрос, смотрите на картинки и выбирайте ту,'
                                    ' которая вам ближе и больше нравится.\n'
                                    'После ответа на все вопросы наш специально обученный искуственный интеллект с помощью сложных расчетов и натальных карт'
                                    ' свяжется с духами предков и определит Ваше тотемное животное!',
                               chat_id=message.chat.id, reply_markup=quiz_menu)


@dp.message_handler(Text("Начали"))
async def quiz(message: types.Message):
    user_id = message.from_user.id
    Sessions.add_session(engine, user_id)
    Scores.add_scores(engine, user_id)

    await bot.send_message(reply_markup=quiz_stop, text='для отмены нажмите кнопку ниже', chat_id=message.chat.id)
    photo = open('images/questions/q1.jpg', mode='+rb')
    await message.answer_photo(caption=questions[0][0], photo=photo, reply_markup=quiz_buttons(0))


@dp.message_handler(Text("Продолжить"))
async def continue_quiz(message: types.Message):
    user_id = message.from_user.id
    if Sessions.check_session(engine, user_id):
        sess = Sessions.get_session(engine, user_id)
        if sess.at_welcome:
            sess.at_welcome = 0
            await bot.send_message(reply_markup=quiz_stop, text='для отмены нажмите кнопку ниже',
                                   chat_id=message.chat.id)
            path = f'images/questions/q{sess.cur_qst_num + 1}.jpg'
            photo = open(path, mode='+rb')

            await message.answer_photo(caption=questions[sess.cur_qst_num][0], photo=photo,
                                       reply_markup=quiz_buttons(sess.cur_qst_num))

            Sessions.save(engine, sess)


@dp.message_handler(Text("Отмена"))
async def cancel_quiz(message: types.Message):
    user_id = message.from_user.id
    if Sessions.check_session(engine, user_id):
        s = Sessions.get_session(engine, user_id)
        if s.is_comment:
            await message.answer("Написание отзыва было отменено.", reply_markup=bot_menu)
            Sessions.del_session(engine, user_id)
        else:
            await message.answer("Вы всегда можете вернуться и пройти Викторину еще раз", reply_markup=bot_menu)


@dp.message_handler(Text("Остановить игру"))
async def stop_quiz(message: types.Message):
    await message.answer("Вы всегда можете вернуться и продолжить Викторину", reply_markup=bot_menu)


@dp.message_handler(Text("Сбросить"))
async def drop_quiz(message: types.Message):
    user_id = message.from_user.id
    Sessions.del_session(engine, user_id)
    Scores.del_scores(engine, user_id)
    await message.answer("Вы всегда можете вернуться и продолжить Викторину", reply_markup=bot_menu)


@dp.message_handler(Text("Купить билеты"))
async def buy_tickets(message: types.Message):
    await message.answer("https://www.mos.ru/afisha/event/414257/", reply_markup=bot_menu)


@dp.message_handler(Text("Узнать о круге друзей"))
async def circle_of_friends(message: types.Message):
    await message.answer("https://www.justbenice.ru/work/moscowzoo/", reply_markup=bot_menu)


@dp.message_handler(Text("Связаться с  нами"))
async def contacts(message: types.Message):
    await message.answer("Если вы хотите стать другом Московского зоопарка или хотите взять свое Тотемное животное под "
                         "опеку, то можете связаться с нами и мы подскажем как это сделать и ответим на любые вопросы\n"
                         "+7(958)813-15-60 \n"
                         "a.sharapova@moscowzoo.ru", reply_markup=bot_menu)


@dp.message_handler(Text("Оставить отзыв"))
async def review_quiz(message: types.Message):
    user_id = message.from_user.id
    await message.answer('Если вы хотите оставить отзыв, то отправьте сообщение с текстом отзыва. '
                         'Для отмены нажмите кнопку "Отмена".', reply_markup=review_cancel)
    s = Sessions(user_id=user_id, is_comment=True)
    Sessions.save(engine, s)


@dp.message_handler()
async def review_quiz(message: types.Message):
    user_id = message.from_user.id
    if Sessions.check_session(engine, user_id):
        s = Sessions.get_session(engine, user_id)
        if s.is_comment:
            c = Reviews(review=message.text)
            Reviews.save(engine, c)
            await message.answer('Спасибо за оставленный отзыв.', reply_markup=bot_menu)
            Sessions.del_session(engine, user_id)


@dp.callback_query_handler()
async def quiz_answer(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if "system" in callback_query.data:
        if "mail" in callback_query.data:
            send_mail(os.environ.get("TO_MAIL"), os.environ.get("FROM_MAIL"), os.environ.get("MAIL_PASSWORD"), callback_query.from_user.username, callback_query.data.split("system.mail.")[1])
    elif Sessions.check_session(engine, user_id):
        sess = Sessions.get_session(engine, user_id)
        qst = questions[sess.cur_qst_num][1][callback_query.data]
        Scores.update_scores(engine, user_id, qst["category"], qst["value"])

        sess.cur_qst_num += 1

        if sess.cur_qst_num < len(questions):
            path = f'images/questions/q{sess.cur_qst_num + 1}.jpg'
            photo = open(path, mode='+rb')
            await bot.edit_message_media(
                media=types.InputMedia(type='photo', media=photo, caption=questions[sess.cur_qst_num][0]),
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=quiz_buttons(sess.cur_qst_num))
            Sessions.save(engine, sess)
        else:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)

            our_scores = Scores.get_scores(engine, user_id)
            totem = choose(scores, categories, our_scores)
            msg = final_message(our_scores)
            keyboard = types.InlineKeyboardMarkup()
            button_link = types.InlineKeyboardButton(text="Узнать про свое тотемное животное больше", url=links[totem])
            button_mail = types.InlineKeyboardButton(text="Отправить письмо с просьбой об опеке.", callback_data="system.mail."+totem)
            keyboard.add(button_link)
            keyboard.add(button_mail)
            path = f'images/animals/{totem}.jpg'
            photo = open(path, mode='+rb')
            await bot.send_message(chat_id=callback_query.message.chat.id, text=msg)
            await bot.send_photo(chat_id=callback_query.message.chat.id, photo=photo)
            await bot.send_message(chat_id=callback_query.message.chat.id, text=descriptions[totem],
                                   reply_markup=keyboard)
            await bot.send_message(chat_id=callback_query.message.chat.id, text="Поздравляю Вы узнали свой тотем!!!\n"
                                                                                "Вы можете написать нам и узнать, как взять свое тотемное животное под опеку.\n"
                                                                                "А если хотите - то можно пройти тест еще раз!\n"
                                                                                "А еще можно купить билет в зоопарк и весело провести время!"
                                   , reply_markup=bot_menu)
            Sessions.del_session(engine, user_id)
            Scores.del_scores(engine, user_id)
            Statistics.update_score(engine, totem)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)

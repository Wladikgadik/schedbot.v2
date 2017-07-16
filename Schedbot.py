import telebot
import config


if (__name__ == '__main__'):
    bot = telebot.TeleBot(config.tokenString)

@bot.message_handler(commands=['start'])
def handle_text(message):
    #user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup = telebot.types.InlineKeyboardMarkup()
    #user_markup.add(*[telebot.types.InlineKeyboardButton(text=name, callback_data=name) for name in [['Расписание студентов'],
                                                                                                       # ['Расписание преподавателей'],
                                                                                                 # ['Занятость аудиторий'],
                                                                                                       # ['Избранное'],
                                                                                                       # ['Отзыв', 'Обратная связь']]])
    user_markup.row(
        telebot.types.InlineKeyboardButton(text='Расписание студентов 👨‍🎓 👩‍🎓', callback_data='Расписание студентов'))
    user_markup.row(
        telebot.types.InlineKeyboardButton(text='Расписание преподавателей 👨‍🏫 👩‍🏫', callback_data='Расписание преподавателей'))
    user_markup.row(
        telebot.types.InlineKeyboardButton(text='Занятость аудиторий ⏰', callback_data='Занятость аудиторий'))
    user_markup.row(
        telebot.types.InlineKeyboardButton(text='Избранное 💾', callback_data='Избранное'))
    user_markup.row(
        telebot.types.InlineKeyboardButton(text='Отзыв 📝', callback_data='Отзыв'),
        telebot.types.InlineKeyboardButton(text='Обратная связь ☎️', callback_data='Обратная связь'))


    bot.send_message(message.from_user.id, 'Выберите пункт меню:', reply_markup=user_markup)
#@bot.message_handler(func=lambda message: True, content_types=["text"])
@bot.callback_query_handler(func=lambda message: True)
def repeat_all_messages(message):
    bot.send_message(message.message.chat.id, message.data)

if __name__ == '__main__':
    bot.polling(none_stop=True)

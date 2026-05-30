import telebot
from telebot import types

# Вставь сюда свой токен
BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА"
# Ссылка на твой сайт из GitHub Pages
GITHUB_WEBAPP_URL = "https://tima1225.github.io/Sale/" 

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = types.WebAppInfo(url=GITHUB_WEBAPP_URL)
    markup.add(types.KeyboardButton(text="🛍 Открыть Каталог", web_app=web_app))
    
    bot.send_message(
        message.chat.id, 
        "🇨🇳 **China Express приветствует вас!**\n\nНажмите на кнопку ниже, чтобы открыть каталог.", 
        reply_markup=markup,
        parse_mode="Markdown"
    )

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()

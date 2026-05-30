import telebot
from telebot import types
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# =================================================================
# ВНИМАТЕЛЬНО ЗАПОЛНИ ЭТИ ДВЕ СТРОЧКИ:
BOT_TOKEN = "8837513824:AAGUe9BP5mWDqHtFRkxsYp3Km6fmNexRk5U"
ADMIN_ID = "8837513824"
# =================================================================

bot = telebot.TeleBot(BOT_TOKEN)

# Локальная тестовая база товаров
PRODUCTS = [
    {"id": 1, "category": "shoes", "title": "Nike Dunk Low Retro", "price": 9200, "oldPrice": 16500, "type": "in_stock", "sizes": ["41", "42", "43", "44"], "img": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=500&q=80"},
    {"id": 2, "category": "clothes", "title": "Куртка TNF Baltoro Black", "price": 14500, "oldPrice": 28000, "type": "on_order", "sizes": ["S", "M", "L", "XL"], "img": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&q=80"}
]

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Кнопка WebApp, которая откроет наш сайт внутри ТГ
    web_app = types.WebAppInfo(url="http://localhost:8080")
    markup.add(types.KeyboardButton(text="🛍 Открыть Каталог", web_app=web_app))
    
    bot.send_message(
        message.chat.id, 
        "✅ **Система China Express запущена!**\n\nНажмите на кнопку ниже, чтобы открыть премиальный слайдер со шрифтом Century Gothic.", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

# Принятие оформленного заказа из WebApp сайта
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    data = json.loads(message.web_app_data.data)
    
    order_text = (
        f"🛍 **Новый заказ в системе!**\n\n"
        f"👤 Получатель: {data['customer_name']}\n"
        f"📞 Телефон: {data['customer_phone']}\n"
        f"📍 СДЭК: {data['customer_address']}\n\n"
        f"📦 **Товары:**\n{data['items']}\n\n"
        f"💰 Итого к оплате: **{data['total']} ₽**\n\n"
        f"💳 Переведите сумму на карту и пришлите чек в этот чат."
    )
    # Отправляем клиенту
    bot.send_message(message.chat.id, order_text, parse_mode="Markdown")
    # Дублируем тебе как админу
    if str(message.chat.id) != str(ADMIN_ID):
        bot.send_message(ADMIN_ID, f"🚨 **Уведомление для админа!**\n\n{order_text}", parse_mode="Markdown")

# ВЕБ-СЕРВЕР ДЛЯ ПЕРЕДАЧИ ДАННЫХ НА САЙТ
class LocalServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/api/products':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(PRODUCTS).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server = HTTPServer(('localhost', 8080), LocalServer)
    print("🔥 Локальный веб-сервер успешно запущен на порту 8080!")
    server.serve_forever()

if __name__ == '__main__':
    # Запускаем сайт в отдельном потоке, чтобы он не мешал боту
    threading.Thread(target=run_server, daemon=True).start()
    print("⏳ Бот подключается к Telegram... Ждите.")
    bot.infinity_polling()
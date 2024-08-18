import telebot
import random
import time
import os
from dotenv import load_dotenv
from PIL import Image
import io

# Загрузка переменных окружения из файла .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота
bot = telebot.TeleBot(TOKEN)
# Максимальное количество попыток для отправки сообщений
MAX_RETRIES = 5

# Функция для отправки сообщений с повторной попыткой
def send_message_with_retry(chat_id, text):
    for attempt in range(MAX_RETRIES):
        try:
            bot.send_message(chat_id, text)
            break
        except telebot.apihelper.ApiTelegramException as e:
            if e.description == "Too Many Requests: retry after X":
                retry_after = int(str(e).split()[-1])
                time.sleep(retry_after + 1)
            else:
                raise e
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise e
            else:
                time.sleep(2)  # Пауза перед повторной попыткой

def play_round(message):
    safe_send_message(bot, message.chat.id, "Введите /next, чтобы перейти к следующему раунду.")

# Список всех возможных событий
events = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "46", "48", "48", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62"]

# Количество раундов
num_rounds = 10

# Глобальные переменные для игры
available_events = []
round_count = 0
game_active = False
current_round_events = []

# Функция для сжатия изображения
def compress_image(image_path):
    with Image.open(image_path) as img:
        img.thumbnail((1024, 1024))  # Измените размер изображения
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)  # Измените качество изображения
        buffer.seek(0)
        return buffer

# Функция для начала игры
@bot.message_handler(commands=['start'])
def start_game(message):
    global available_events, round_count, game_active, current_round_events
    available_events = events.copy()
    random.shuffle(available_events)
    round_count = 1
    game_active = True
    current_round_events = []

    bot.reply_to(message, "Добро пожаловать в игру! Приготовьтесь к захватывающему приключению.")
    play_round(message)

# Функция для проведения одного раунда
def play_round(message):
    global round_count, game_active, current_round_events

    # Сообщение о начале раунда
    bot.reply_to(message, f"Раунд {round_count}:")

    # Обнуление текущих событий
    current_round_events = []

    # Добавляем уникальные события в текущий раунд
    while len(current_round_events) < min(3, len(available_events)):
        new_event = random.choice(available_events)
        if new_event not in current_round_events:
            current_round_events.append(new_event)
            available_events.remove(new_event)

    display_events(message)

    # Проверяем, остались ли раунды
    if round_count == num_rounds:
        bot.reply_to(message, "Игра окончена! Спасибо за участие.")
        game_active = False
    else:
        bot.reply_to(message, "Введите /next, чтобы перейти к следующему раунду.")
        round_count += 1
    # Функция для отображения событий раунда
def display_events(message):
    global current_round_events
    for event in current_round_events:
        event_image = f"{event.replace(' ', '_')}.jpg"
        image_path = os.path.join("events", event_image)
        if os.path.exists(image_path):
            compressed_image = compress_image(image_path)
            bot.send_photo(chat_id=message.chat.id, photo=compressed_image)
        else:
            bot.reply_to(message, event)

@bot.message_handler(commands=['next'])
def handle_next_round(message):
    global game_active

    if game_active:
        play_round(message)
    else:
        bot.reply_to(message, "Игра уже окончена. Введите /start, чтобы начать новую игру.")

@bot.message_handler(commands=['roll'])
def handle_roll(message):
    global game_active, available_events, current_round_events

    if game_active:
        if available_events:
            new_event = random.choice(available_events)
            current_round_events.append(new_event)
            display_events(message)
        else:
            bot.reply_to(message, "Больше нет доступных событий для добавления.")
    else:
        bot.reply_to(message, "Игра уже окончена. Введите /start, чтобы начать новую игру.")

# Обработчик для любых других сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    global game_active
    if game_active:
        bot.reply_to(message, "Извините, я не понимаю этой команды. Введите /next, чтобы перейти к следующему раунду.")
    else:
        bot.reply_to(message, "Игра окончена. Введите /start, чтобы начать новую игру.")

# Запуск бота
bot.infinity_polling()

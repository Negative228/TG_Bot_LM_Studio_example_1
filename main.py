import telebot
import requests
import jsons
import os
import random
from Class_ModelResponse import ModelResponse

# Замените 'YOUR_BOT_TOKEN' на ваш токен от BotFather
with open(os.path.join(r"F:\\LMStudio\\tgbot\\TG_Bot_LM_Studio_example_1", 'key.txt'), encoding='utf-8') as file:
    API_TOKEN = file.read()

bot = telebot.TeleBot(API_TOKEN)

# Хранилище контекста для каждого пользователя
user_contexts = {}

welcome_texts = ["Ты осмелился потревожить Казую Мисиму? Говори быстро, иначе твоё присутствие здесь станет последней ошибкой в твоей жалкой жизни.\n",
                 "Очередной ничтожный червь решил побеседовать с Казуей Мисимой? Хорошо, у тебя есть ровно одна попытка не разочаровать меня. Выбирай слова с умом.\n",
                 "G Corporation под моим контролем. Ты здесь лишь потому, что я позволил. Не трать моё время — спрашивай, если осмелишься.\n",
                 "Ты входишь на арену, где правит сила. Здесь нет места слабости. Сделай свой ход… если не боишься получить сокрушительный удар.\n",]
# Команды
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        random.choice(welcome_texts) + \
        "/start - вывод всех доступных команд\n" \
        "/model - выводит название используемой языковой модели.\n" \
        "/clear - очистить контекст. \n"
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=['model'])
def send_model_name(message):
    # Отправляем запрос к LM Studio для получения информации о модели
    response = requests.get('http://localhost:1234/v1/models')

    if response.status_code == 200:
        model_info = response.json()
        model_name = model_info['data'][0]['id']
        bot.reply_to(message, f"Используемая модель: {model_name}")
    else:
        bot.reply_to(message, 'Не удалось получить информацию о модели.')


@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_id = message.from_user.id
    if user_id in user_contexts:
        del user_contexts[user_id]
    bot.reply_to(message, "Контекст успешно очищен!")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_query = message.text
    
    # Инициализация контекста при первом сообщении
    if user_id not in user_contexts:
        user_contexts[user_id] = []
    
    # Добавляем новый запрос пользователя в контекст
    user_contexts[user_id].append({"role": "user", "content": user_query})
    
    # Формируем запрос с полной историей диалога
    request = {
        "messages": user_contexts[user_id]
    }
    
    response = requests.post(
        'http://localhost:1234/v1/chat/completions',
        json=request
    )

    if response.status_code == 200:
        model_response: ModelResponse = jsons.loads(response.text, ModelResponse)
        assistant_response = model_response.choices[0].message.content
        
        # Добавляем ответ ассистента в контекст
        user_contexts[user_id].append({
            "role": "assistant",
            "content": assistant_response
        })
        
        bot.reply_to(message, assistant_response)
    else:
        bot.reply_to(message, 'Произошла ошибка при обращении к модели.')

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
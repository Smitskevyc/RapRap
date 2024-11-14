import asyncio
from telethon import TelegramClient, events

# Данные для первого аккаунта (чтение сообщений)
API_ID_2 = 28670148
API_HASH_2 = '77b2ee6f754921e6db7cc3f995e3da56'
PHONE_NUMBER_2 = '+380633890119'

# Данные для второго аккаунта (отправка сообщений в @CryptoBot)
API_ID_1 = 29927044  # Замените на API ID второго аккаунта
API_HASH_1 = 'a5bec5dba2cea639c9924b496f568486'
PHONE_NUMBER_1 = '+380631155275'  # Номер второго аккаунта

# ID чата, который нужно отслеживать
CHAT_ID_TO_MONITOR = -1001997427373  # Замените на нужный ID

# Создаем клиенты для обоих аккаунтов
client_reader = TelegramClient('reader_session', API_ID_1, API_HASH_1)
client_sender = TelegramClient('sender_session', API_ID_2, API_HASH_2)

# Функция для проверки и нажатия на кнопку с текстом "Получить"
async def monitor_button(event):
    message = event.message

    if not message.buttons and '🕒' not in message.message:
        print("Нет кнопок и нет смайлика 🕒 в сообщении.")
        return

    max_checks = 200
    check_count = 0

    while check_count < max_checks:
        message = await client_reader.get_messages(message.chat_id, ids=message.id)

        if '🕒' in message.message:
            print("Сообщение содержит смайлик 🕒, обновляем кнопки...")

        if message.buttons:
            for row in message.buttons:
                for button in row:
                    if "Получено" in button.text:
                        print("Сообщение уже обработано, пропускаем.")
                        return

                    elif "Получить" in button.text:
                        print(f"Найдена кнопка с текстом '{button.text}'. Извлекаем ссылку...")

                        if button.url:
                            code = button.url.split("start=")[-1]
                            print(f"Получен код: {code}")

                            # Отправляем команду во втором клиенте
                            await client_sender.send_message('@CryptoBot', f'/start {code}')
                            print("Код отправлен в @CryptoBot со второго аккаунта.")
                        else:
                            print("Ссылка не найдена.")
                        return
                    elif "..." in button.text:
                        print("Кнопка ещё формируется, ждём обновления...")
                    else:
                        print(f"Кнопка с текстом '{button.text}' не требует действий.")

        check_count += 1
        await asyncio.sleep(0.01)

    if check_count >= max_checks:
        print("Достигнуто максимальное количество проверок, завершаем мониторинг этого сообщения.")

# Главная функция для запуска обоих клиентов
async def main():
    await client_reader.start(phone=PHONE_NUMBER_1)
    await client_sender.start(phone=PHONE_NUMBER_2)
    print("Оба клиента подключены к Telegram.")

    @client_reader.on(events.NewMessage(chats=CHAT_ID_TO_MONITOR))
    async def monitor_messages(event):
        message_text = event.message.message
        print(f"Новое сообщение: {message_text}")

        await monitor_button(event)

    await client_reader.run_until_disconnected()
    await client_sender.run_until_disconnected()

# Запускаем клиентов
asyncio.run(main())

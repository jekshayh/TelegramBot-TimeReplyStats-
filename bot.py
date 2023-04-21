import logging
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import matplotlib.pyplot as plt
import io

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile


API_TOKEN = 'a_place_for_your_token'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


conn = sqlite3.connect('bot.db')
c = conn.cursor()


c.execute('''CREATE TABLE IF NOT EXISTS questions
             (id INTEGER PRIMARY KEY, message_id INTEGER, time TIMESTAMP)''')

c.execute('''CREATE TABLE IF NOT EXISTS answers
             (id INTEGER PRIMARY KEY, message_id INTEGER, answer_id INTEGER, time TIMESTAMP, sender_id INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS reg_curators
             (id INTEGER PRIMARY KEY, cur_id INTEGER)''')
conn.commit()

@dp.message_handler(commands=['future_password'])
async def send_welcome(message: types.Message):
    c.execute("SELECT * FROM reg_curators WHERE cur_id=?", (message.from_user.id,))
    result = c.fetchone()
    if result:
        await message.answer("Вы уже зарегистрированы!")
        return
    
    c.execute("INSERT INTO reg_curators (cur_id) VALUES (?)", (message.from_user.id,))
    conn.commit()
    await message.answer("Теперь вы зарегистрированы как куратор!")

@dp.message_handler()
async def handle_message(message: types.Message):

    c.execute("SELECT * FROM reg_curators WHERE cur_id=?", (message.from_user.id,))
    check = c.fetchone()

    # если сообщение не от куратора
    if check is None:    
        if "?" in message.text:
            
            # записываем id вопроса и когда он был отправлен
            message_id = message.message_id
            message_date = message.date

            c.execute("INSERT INTO questions (message_id, time) VALUES (?, ?)", (message_id, message_date))
            conn.commit()
    # если сообщение от куратора
    else:
        # если это ответ
        if message.reply_to_message is not None:
            
            answered_message_id = message.reply_to_message.message_id

            c.execute("SELECT * FROM questions WHERE message_id=?", (answered_message_id,))
            
            # проверяем что это реплай на вопрос, а не на какое-то другое сообщение
            if c.fetchone() is not None:
                
                message_id = message.message_id
                message_date = message.date
                curator_id = message.from_user.id

                c.execute("INSERT INTO answers (message_id, answer_id, time, sender_id) VALUES (?, ?, ?, ?)", (answered_message_id, message_id, message_date, curator_id))
                conn.commit()
        else:
            if message.text == "stats":
                c.execute("SELECT DISTINCT sender_id FROM answers")
                sender_ids = [row[0] for row in c.fetchall()]
                rows_by_sender_id = defaultdict(list)
                for sender_id in sender_ids:
                    c.execute("""SELECT questions.time, answers.time
                            FROM questions JOIN answers ON questions.message_id = answers.message_id
                            WHERE answers.sender_id = ?""", (sender_id,))
                    rows = c.fetchall()

                    for row in rows:
                        time_format = "%Y-%m-%d %H:%M:%S"
                        time1 = datetime.strptime(row[0], time_format)
                        time2 = datetime.strptime(row[1], time_format)
                        time_diff = time2 - time1
                        rows_by_sender_id[sender_id].append(time_diff)

                
                avg_time_graph = []
                for sender_id, time_diffs in rows_by_sender_id.items():
                    total_time = sum(time_diffs, timedelta())
                    avg_time = (total_time / len(time_diffs))
                    avg_time_graph.append(avg_time.total_seconds()/60)


                
                senders_graph = []
                for i in sender_ids:
                    senders_graph.append(str(i))


                plt.bar(senders_graph, avg_time_graph, color='blue', width=0.4)
                plt.xlabel('Curator')
                plt.ylabel('Average Time of Reply in Minutes')
                plt.title('Average Time of Reply by Curator')

 

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)

                
                photo = InputFile(buf)
                await message.reply_photo(photo=photo)
              
                    
                        
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

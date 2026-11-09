from datetime import datetime
import os
from threading import Thread
import ARtts
from flask import Flask
from google import genai
import ENtts
import qr
import remove
import telebot
import usd
import matches

app = Flask('')


@app.route('/')
def home():
  return 'Bot is running!'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


Thread(target=run).start()

import sqlite3

admin_id = '5985236910'
bot = telebot.TeleBot('your telegram API')
bot.remove_webhook()
user_ai_mode = {}

# --- إعداد قاعدة البيانات ---
try:
  with sqlite3.connect('bot.db', timeout=10) as db:
    cr = db.cursor()
    cr.execute(
        'create table if not exists users(name text , user_name text , uid integer'
        ' primary key)'
    )
    cr.execute('pragma foreign_keys=on')
    cr.execute(
        'create table if not exists orders( name text, uid integer , order_time'
        ' text , [order] text)'
    )
    cr.execute(
        'create table if not exists notes(name text ,uid integer,note'
        ' text,note_time , foreign key (uid) references users (uid))'
    )
    db.commit()
except Exception as e:
  print(f'ERROR IN DATABASE : {e}')


def save_order(name, uid, order_time, order):
  try:
    with sqlite3.connect('bot.db', timeout=10) as db:
      cr = db.cursor()
      cr.execute(
          'insert into orders(name , uid , order_time , [order]) values (? , ? ,'
          ' ? , ?)',
          (name, uid, order_time, order),
      )
      db.commit()
  except Exception as e:
    print(f'ERROR IN DATABASE : {e}')


# --- الدوال المساعدة ---
def handel_qr(message):
  if message.text and message.text.startswith('/'):
    return
  uid = message.chat.id
  name = message.from_user.first_name
  qr.generate(uid, message.text, bot)


def handel_ar(message):
  uid = message.chat.id
  try:
    ARtts.send_ar(uid, bot, message)
  except Exception as e:
    bot.send_message(
        uid, f'Erorr : {e} انسخ النص المكتوب بالانكليزي و ابعته بزر الملاحظة'
    )


def handel_en(message):
  uid = message.chat.id
  try:
    ENtts.send_eng(uid, bot, message)
  except Exception as e:
    bot.send_message(
        uid,
        f'Erorr : {e} \n انسخ النص الظاهر باللغة الانكليزية و ابعته في زر ملاحظة'
        ' ليتم اصلاح المشكلة',
    )


def ai_response(uid, text, bot):
  client = genai.Client(
      api_key='your AI API'
  )

  system_instruction = """
    أنت مساعد ذكي رقمي تم تطويرك وبرمجتك بواسطة المبرمج علي. 
    إذا سألك أي شخص عن الجهة التي طورتك أو صنعتك، يجب أن تجيب بوضوح بأنك مساعد شخصي تم تطويرك بواسطة علي وليس بواسطة أي جهة أخرى.
    كن دائماً دقيقاً، لطيفاً، ومختصراً في إجاباتك.
    """

  primary_model = 'gemini-3.5-flash'
  fallback_model = 'gemini-1.5-flash'

  try:
    response = client.models.generate_content(
        model=primary_model,
        contents=text,
        config={'system_instruction': system_instruction},
    )
    bot.send_message(uid, response.text)

  except Exception as e:
    try:
      response = client.models.generate_content(
          model=fallback_model,
          contents=text,
          config={'system_instruction': system_instruction},
      )
      bot.send_message(
          uid,
          f'⚠️ ملاحظة: النموذج الأساسي يواجه ضغطاً حالياً، تم العثور على نموذج'
          f' بديل وتفعيل الاستجابة:\n\n{response.text}',
      )

    except Exception as fallback_error:
      bot.send_message(
          uid, 'عذراً، الخدمة تشهد ضغطاً شديداً حالياً، يرجى المحاولة بعد قليل.'
      )


# --- أوامر البوت ---
@bot.message_handler(commands=['start'])
def welcome(message):
  order = 'start'
  uid = message.chat.id
  name = message.from_user.first_name
  usname = message.from_user.username
  request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  print(f'{name} started bot at {request_time}')
  try:
    db = sqlite3.connect('bot.db')
    cr = db.cursor()
    cr.execute(
        'insert into users(name ,user_name , uid) values (? ,? , ?)',
        (name, usname, uid),
    )
    db.commit()
    save_order(name, uid, request_time, order)
    bot.send_message(
        admin_id,
        f'New user at {request_time}\nname: {name}\nuser : {usname}\nID : {uid}',
    )
  except:
    pass

  bot.send_message(
      uid,
      '✨ أهلاً بك في عالم NEXUS ⚡\n\nمساعدك الرقمي الشامل والمتطور، مصمم ليجمع لك'
      ' كل ما تحتاجه في مكان واحد وبأعلى سرعة وسلاسة.\n\nإليك قائمة الخدمات والأوامر'
      ' المتاحة حالياً:\n⚽ /match - عرض مباريات اليوم والنتائج لحظة'
      ' بلحظة.\n💱 /currency - متابعة سعر الدولار بالليرة السورية.\n🔲 /qr -'
      ' توليد أكواد QR نصية بدقة وسرعة.\n🎙 /voice - تحويل النصوص المكتوبة إلى'
      ' مقاطع صوتية واضحة.\n🖼 /bg - إزالة خلفية الصور بدقة وبشكل احترافي.\n🧠 /ai'
      ' - التحدث مع المساعد الذكي والمتقدم.\n\n📌 كيف تبدأ؟\nببساطة، يمكنك الضغط'
      ' على زر القائمة (Menu) بجانب حقل الرسائل لاختيار الأمر الذي تريده، أو'
      ' كتابة الأمر مباشرة في المحادثة! 🚀\n\n---\n🛠 تم التطوير بواسطة: @Ali076s',
  )


@bot.message_handler(commands=['match'])
def send_matches(message):
  uid = message.chat.id
  name = message.from_user.first_name
  request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  order = 'match'
  matches.matches_codes(uid, bot)
  print(f'{name} clicked on {order} at {request_time}\nID : {uid}')
  bot.send_message(
      admin_id,
      f'New order \nname : {name}\ntime : {request_time}\norder : {order}',
  )
  save_order(name, uid, request_time, order)


@bot.message_handler(commands=['currency'])
def send_usd(message):
  uid = message.chat.id
  name = message.from_user.first_name
  request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  order = 'currency'
  usd.get_usd(uid, bot)
  bot.send_message(
      admin_id,
      f'New order\nname : {name}\nTime : {request_time}\norder : {order}',
  )
  save_order(name, uid, request_time, order)


@bot.message_handler(commands=['getdb'])
def send_database_file(message):
  ADMIN_ID = 5985236910
  if message.from_user.id == ADMIN_ID:
    try:
      db_name = 'bot.db'
      basedir = os.path.abspath(os.path.dirname(__file__))
      db_path = os.path.join(basedir, db_name)

      if os.path.exists(db_path):
        with open(db_path, 'rb') as db_file:
          bot.send_document(
              message.chat.id,
              db_file,
              caption='📂 هذه نسخة احتياطية لقاعدة البيانات',
          )
      else:
        bot.reply_to(
            message,
            '❌ لم يتم العثور على ملف قاعدة البيانات بهذا الاسم في المجلد.',
        )
    except Exception as e:
      bot.reply_to(message, f'حدث خطأ أثناء إرسال الملف: {e}')
  else:
    bot.reply_to(message, 'عذراً، هذا الأمر مخصص للمسؤول فقط.')


@bot.message_handler(commands=['voice'])
def send_tts(message):
  uid = message.chat.id
  name = message.from_user.first_name
  order = 'voice'
  request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  print(f'{name} clicked on {order} at {request_time}\nID : {uid}')
  bot.send_message(
      admin_id,
      f'New order\nname : {name}\ntime : {request_time}\norder : {order}',
  )
  save_order(name, uid, request_time, order)
  main_markup = telebot.types.InlineKeyboardMarkup()
  b1 = telebot.types.InlineKeyboardButton('AR🇸🇦', callback_data='1')
  b2 = telebot.types.InlineKeyboardButton('EN🇺🇸', callback_data='2')
  main_markup.add(b1)
  main_markup.add(b2)
  bot.send_message(
      uid, 'تنبيه ⚠️: ابعت النص باللغة يلي اخترتها', reply_markup=main_markup
  )


# تم نقل المعالج للخارج (ليس داخل الدالة)
@bot.callback_query_handler(func=lambda call: call.data in ['1', '2'])
def handel_lang(call):
  if call.data == '1':
    ms = bot.send_message(
        call.message.chat.id, 'ارسل النص ليتم تحويله ألى صوت🗣'
    )
    bot.register_next_step_handler(ms, handel_ar)
  elif call.data == '2':
    ms = bot.send_message(
        call.message.chat.id, 'ارسل النص ليتم تحويله ألى صوت.🗣'
    )
    bot.register_next_step_handler(ms, handel_en)
  try:
    bot.answer_callback_query(call.id)
  except:
    pass


@bot.message_handler(commands=['bg'])
def send_noback(message):
  uid = message.chat.id
  name = message.from_user.first_name
  order = 'bg'
  request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  print(f'{name} clicked on {order} at {request_time}\nID : {uid}')
  bot.send_message(
      admin_id,
      f'New order\nname : {name}\ntime : {request_time}\norder : {order}',
  )
  save_order(name, uid, request_time, order)
  msg = bot.send_message(uid, 'أرسل صورة')
  bot.register_next_step_handler(msg, handel_photo)


def handel_photo(message):
  uid = message.chat.id
  try:
    if message.photo:
      file_info = bot.get_file(message.photo[-1].file_id)
      downloaded_file = bot.download_file(file_info.file_path)
      os.makedirs('downloads', exist_ok=True)
      input_path = f'downloads/with_back_{uid}.jpg'

      with open(input_path, 'wb') as new_file:
        new_file.write(downloaded_file)
      remove.remov_back(uid, input_path, bot)
    else:
      bot.send_message(uid, '⚠️ الرجاء إرسال صورة صحيحة.')
  except Exception as e:
    bot.send_message(uid, f'⚠️ حدث خطأ أثناء استقبال الصورة: {e}')


@bot.message_handler(commands=['qr'])
def ask_qr(message):
  ms = bot.send_message(message.chat.id, 'أرسل نص أو رابط')
  bot.register_next_step_handler(ms, handel_qr)
  name = message.from_user.first_name
  uid = message.chat.id
  request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  order = 'qr'
  print(f'{name} clicked on {order} at {request_time}\nID : {uid}')
  bot.send_message(
      admin_id,
      f'New order\nname : {name}\ntime : {request_time}\norder : {order}',
  )
  save_order(name, uid, request_time, order)


@bot.message_handler(commands=['note'])
def get_note(message):
  uid = message.chat.id
  order = 'note'
  name = message.from_user.first_name
  username = message.from_user.username
  request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  print(f'{name} clicked on {order} at {request_time}\nID : {uid}')
  save_order(name, uid, request_time, order)
  msg = bot.send_message(uid, 'تفضل')
  bot.register_next_step_handler(msg, save_note)


def save_note(message):
  uid = message.chat.id
  name = message.from_user.first_name
  request_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  note = message.text
  bot.send_message(uid, '✅تم حفظ الملاحظة سيتم الرد قريبا ....')
  try:
    bot.send_message(
        admin_id,
        f'📍NEW NOTE📍\nFrom : {name}\nat : {request_time}\nID :'
        f' {uid}\nNote : {note}',
    )
    with sqlite3.connect('bot.db', timeout=10) as db:
      cr = db.cursor()
      cr.execute(
          'insert into notes(name , uid , note , note_time) values (? , ? , ? ,'
          ' ?)',
          (name, uid, note, request_time),
      )
      db.commit()

  except Exception as e:
    bot.send_message(
        admin_id,
        f'error in saving a note from user : {name}\nnote : {note}       {e}',
    )


@bot.message_handler(commands=['ai'])
def get_ans(message):
  uid = message.chat.id
  user_ai_mode[uid] = True
  bot.send_message(
      uid,
      '✨ تم فتح محادثة الذكاء الاصطناعي المستمرة. أرسل ما شئت، وللخروج أرسل /exit',
  )


@bot.message_handler(commands=['exit'])
def exit_ai(message):
  uid = message.chat.id
  if uid in user_ai_mode:
    del user_ai_mode[uid]
  bot.send_message(uid, 'تم إنهاء محادثة الذكاء الاصطناعي. ✅')


# معالج عام للرسائل النصية (مستقل وبدون تداخل مسافات)
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
  uid = message.chat.id
  if uid in user_ai_mode:
    msg = message.text
    ai_response(uid, msg, bot)
  else:
    bot.send_message(
        uid, 'الرجاء اختيار أمر من القائمة أو الضغط على /ai للبدء بالمحادثة.'
    )


print('\n' * 2)
print('			BOT IS RUNING		')
print('\n' * 2)
print('*' * 70)
bot.infinity_polling(none_stop=True)

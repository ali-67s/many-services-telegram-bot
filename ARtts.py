import os
from gtts import gTTS


def send_ar(uid, bot, message): 
  ms = message.text

  if ms and ms.startswith("/"):
    return

  file_path = f"downloads/voice_{uid}.mp3"

  try:
    if not os.path.exists("downloads"):
      os.makedirs("downloads")

    tts = gTTS(text=ms, lang="ar", slow=False)
    tts.save(file_path)
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
      with open(file_path, "rb") as v:
        bot.send_voice(uid, v, caption="🎙️ الصوت جاهز")
    else:
      bot.send_message(uid, "عفواً، لم يتم حفظ ملف الصوت.")

  except Exception as e:
    bot.send_message(uid, f"حدث خطأ: {e}")

  finally:
   
    if os.path.exists(file_path):
      os.remove(file_path)

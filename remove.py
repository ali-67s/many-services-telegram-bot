import os
import requests

def remov_back(uid, photo_path, bot):
    output_path = f"downloads/no_bg_{uid}.png"
    
    try:
        # التأكد من وجود مجلد التحميلات
        os.makedirs("downloads", exist_ok=True)
        
        # إرسال رسالة للمستخدم بأن العملية قيد المعالجة
        processing_msg = bot.send_message(uid, "جار ازالة الخلفية...يرجى الانتظار⏳")
        
        # رابط خدمة إزالة الخلفية الشهيرة
        api_url = "your API"
        
        # ضع مفتاح الـ API المجاني الخاص بك هنا بين القوسين
        api_key = "bieMW4R3QMctu5mXP9FxFT16"
        
        with open(photo_path, 'rb') as image_file:
            response = requests.post(
                api_url,
                files={'image_file': image_file},
                data={'size': 'auto'},
                headers={'X-Api-Key': api_key}
            )
            
        # التحقق من نجاح العملية
        if response.status_code == 200:
            with open(output_path, 'wb') as out_file:
                out_file.write(response.content)
                
            # إرسال الصورة الناجحة بخلفية شفافة
            with open(output_path, 'rb') as photo:
                bot.send_photo(uid, photo, caption="✨ تفضل، الصورة جاهزة وبدون خلفية!")
                
            # حذف رسالة الانتظار المؤقتة
            bot.delete_message(uid, processing_msg.message_id)
        else:
            # في حال نفاد الرصيد المجاني أو خطأ في المفتاح
            bot.edit_message_text(
                "❌ حدث خطأ في معالجة الصورة، تأكد من صحة مفتاح الـ API أو رصيدك المجاني.", 
                uid, 
                processing_msg.message_id
            )
            
    except Exception as e:
        bot.send_message(uid, f"حدث خطأ غير متوقع: {e}")
        
    finally:
        # تنظيف وحذف الملفات المؤقتة من الجهاز للمحافظة على الذاكرة
        if os.path.exists(output_path):
            os.remove(output_path)
        if os.path.exists(photo_path):
            os.remove(photo_path)

from datetime import datetime, timedelta
import requests


def matches_data(uid, bot):
  wait_msg = bot.send_message(
      uid, "⏳ **جاري جلب مباريات اليوم في الدوريات الكبرى...**", parse_mode="Markdown"
  )

  try:
    # ضبط التاريخ ليناسب توقيت سوريا المحلي (UTC+3) بدلاً من توقيت السيرفر العالمي
    syria_time = datetime.utcnow() + timedelta(hours=3)
    today_date = syria_time.strftime("%Y-%m-%d")

    url = f"your API={today_date}&dateTo={today_date}"
    headers = {"X-Auth-Token": "636af41e796e483297efd56799b099a1"}

    response = requests.get(url, headers=headers, timeout=10)
    request_code = response.status_code

    if request_code == 200:
      data = response.json()
      matches_list = data.get("matches", [])

      if not matches_list:
        bot.send_message(
            uid,
            (
                f"📭 لا توجد مباريات مسجلة اليوم ({today_date}) في الدوريات"
                " الكبرى المشمولة بالخطة المجانية."
            ),
            parse_mode="Markdown",
        )
        return

      message = f"⚽ **مباريات اليوم ({today_date})** ⚽\n"
      message += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

      for match in matches_list[:6]:
        home = (
            match.get("homeTeam", {}).get("name")
            or match.get("homeTeam", {}).get("shortName")
            or "الفريق المضيف"
        )
        away = (
            match.get("awayTeam", {}).get("name")
            or match.get("awayTeam", {}).get("shortName")
            or "الفريق الضيف"
        )
        utc_time = match.get("utcDate")
        competition = match.get("competition", {}).get(
            "name", "بطولة رسمية"
        )

        if utc_time:
          try:
            dt = datetime.fromisoformat(utc_time.replace("Z", "+00:00"))
            match_time = dt.strftime("%H:%M")
          except Exception:
            match_time = "قريباً"
        else:
          match_time = "قريباً"

        message += f"🏆 **{competition}**\n"
        message += f"⚔️ `{home}` 🆚 `{away}`\n"
        message += f"⏰ الوقت: `{match_time}` UTC\n"
        message += "──────────────────────\n"

      message += "\n📡 **المصدر:** Football-Data.org"
      bot.send_message(uid, message, parse_mode="Markdown")

    else:
      bot.send_message(
          uid,
          f"⚠️ عذراً، رمز الاستجابة من الخادم: `{request_code}`",
          parse_mode="Markdown",
      )

  except Exception as e:
    bot.send_message(
        uid, f"❌ حدث خطأ تقني: `{str(e)[:80]}`", parse_mode="Markdown"
    )

  finally:
    try:
      if wait_msg:
        bot.delete_message(uid, wait_msg.message_id)
    except:
      pass

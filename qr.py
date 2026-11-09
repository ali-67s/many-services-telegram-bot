import requests
from bs4 import BeautifulSoup
def get_usd(uid , bot):
	response=requests.get("https://liranews.info/#google_vignette")
	soup=BeautifulSoup(response.text , "html.parser")
	sell=soup.find("td" ,{"data-ln-type" :"sell" }).text.strip()
	buy=soup.find("td" , {"data-ln-type" : "buy"}).text.strip()
	print(f"buy : {buy}")
	print(f"sell : {sell}")
	bot.send_message(uid , f"شراء : {buy}\nمبيع : {sell}\nالمصدر : موقع ليرة نيوز")

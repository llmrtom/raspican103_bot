from distutils.command.upload import upload
from bs4 import BeautifulSoup
from math import fabs
import requests
import urllib.parse
import pandas
import datetime
import telebot
import calendar

timeIsNotOver = True
bot = telebot.TeleBot('5321362521:AAF9Okzrw0MPtfFsOA0XZYmcC8El9WhggfQ')

def start_and_end_of_week():
    current_date = datetime.datetime.today()
    check_month = calendar.monthrange(current_date.year,current_date.month)[1]
    current_wd = current_date.weekday()
    days_before_we = 6 - current_wd

    if current_date.month != 1:
        ex_check_month = calendar.monthrange(current_date.year,current_date.month-1)[1]
    else:
        ex_check_month = calendar.monthrange(current_date.year - 1, 12)[1]

    if (current_date.day - current_wd) > 0:
        week_start = current_date.today().replace(day= current_date.day - current_wd)
    elif current_date.month != 1 :
        week_start = current_date.today().replace(day= current_date.day - current_wd + ex_check_month, month = current_date.month - 1)
    else:
        week_start = current_date.today().replace(day= current_date.day - current_wd + ex_check_month, month = 12, year = current_date.year - 1)

    if (current_date.day + days_before_we) <= check_month:
        week_end = week_start.replace(day = current_date.day + days_before_we)
    elif week_start.month != 12 :
        week_end = week_start.replace(day = current_date.day + days_before_we - check_month, month = week_start.month + 1 )
    else:
        week_end = week_start.replace(day = current_date.day + days_before_we - check_month, month = 1, year=week_start.year + 1)

    datews = week_start.strftime("%d.%m.%Y")
    datewe = week_end.strftime("%d.%m.%Y")
    return [datews, datewe]


def tm_and_yd():
    current_date = datetime.datetime.today()
    check_month = calendar.monthrange(current_date.year,current_date.month)[1]

    if current_date.month != 1:
        ex_check_month = calendar.monthrange(current_date.year,current_date.month-1)[1]
    else:
        ex_check_month = calendar.monthrange(current_date.year - 1, 12)[1]

    if (current_date.day - 1) > 0:
        yd_date = current_date.today().replace(day= current_date.day - 1)
    elif current_date.month != 1 :
        yd_date = current_date.today().replace(day= current_date.day - 1 + ex_check_month, month = current_date.month - 1)
    else:
        yd_date = current_date.today().replace(day= current_date.day - 1 + ex_check_month, month = 12, year = current_date.year - 1)

    if (current_date.day + 1) <= check_month:
        tm_date = current_date.replace(day = current_date.day + 1)
    elif tm_date.month != 12 :
        tm_date = current_date.replace(day = current_date.day + 1 - check_month, month = current_date.month + 1 )
    else:
        tm_date = current_date.replace(day = current_date.day + 1 - check_month, month = 1, year=current_date.year + 1)
    return [yd_date, tm_date]
numOfTimeStr = 0



def isTime(tag):
    if ((len(tag.text) >= 11) & (len(tag.text) <= 12) & (tag.name == 'td')) : 
        return(True)
    else: 
        timeIsNotOver = False
        return(False)

def isNoTimeTd(tag):
    if (isTime(tag) == False) & (tag.name == 'td') & (tag.text != "Дата") & (tag.text != "Время занятий") : 
        return(True)
    else:
        return(False) 

def isDate(message):
    if (len(message.text) == 10):
        if (message.text[2] == ".") & (message.text[5] == "."):
            return True
    else:
        return False


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "Выбери день в формате ДД.ММ.ГГГГ. Например, 01.01.2022")

@bot.message_handler(content_types=["text"])
def handle_text(message):
    current_date = datetime.datetime.today()
    
    yd_date = tm_and_yd()[0]
    tm_date = tm_and_yd()[1]

    if message.text == "Неделя":
        dates = start_and_end_of_week()
    elif message.text == "Сегодня":
        dates = [current_date.strftime("%d.%m.%Y"), current_date.strftime("%d.%m.%Y")]
    elif message.text == "Завтра":
        dates = [tm_date.strftime("%d.%m.%Y"), tm_date.strftime("%d.%m.%Y")]
    elif isDate(message):
        dates = [message.text,message.text]
    else:
        bot.send_message(message.from_user.id, "Выбери день в формате ДД.ММ.ГГГГ. Например, 01.01.2022")
        return
    uploadParams = {"rtype":1,"group":2261, "exam" : 0, "datafrom" : dates[0], "dataend" : dates[1], "formo" : 0, "allp" : 0, "hour" : 0, "tuttabl" : 0}

    response = requests.post('http://inet.ibi.spb.ru/raspisan/rasp.php', data=uploadParams)

    resp = response.text
    soup = BeautifulSoup(resp, 'lxml')
    allTime = soup.find_all(isTime)
    if allTime == []:
        bot.send_message(message.from_user.id, dates[0][0:5]+"\nВ этот день пар нет")
        return
    allNoTimeTd = soup.find_all(isNoTimeTd)
    i = 0
    str_output = ""
    for tag in allNoTimeTd:
        if len(tag.text)>1:
            if i != 0:
                str_output += (allTime[i-1].text) + "\n"
            else:
                if str_output != "":
                    bot.send_message(message.from_user.id, str_output)
                    str_output=""
            str_output+=(tag.text)+ "\n\n"
            if i >= (len(allTime)):
                i=0
                bot.send_message(message.from_user.id, str_output)
                str_output=""
            else:
                i+=1
        else:
            #if i != 0:
            #    str_output += (allTime[i-1].text) + "\n"
            #else:
            #    if str_output != "":
            #        bot.send_message(message.from_user.id, str_output)
            #        str_output=""
            #str_output+="Пары нет"+ "\n\n"
            if i >= (len(allTime)):
                i=0
            else:
                i+=1

bot.polling(none_stop=True, interval=0)
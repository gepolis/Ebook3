import asyncio
import random
import time
from time import sleep
import httpx
import requests
from django.http import HttpResponse, JsonResponse
import json

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def index(request):
    if request.GET.get("q"):
        answer = http_call(request.GET.get("q"))
        return JsonResponse({"question": request.GET.get("q"), "answer": answer})


def http_call(message):
    global msg
    headers = {
        "Authorization": "MTA2Njg0NDI5OTUxMTIyMjI5NA.GFFjCa.Zbvw84Pp098WHQqJZ2XCvM80GxzYOXCpnGf3uY",
        "content-encoding": "utf-8",
    }
    msg_id = f"{random.randint(10000000, 99999999)}{round(time.time())}"

    save = ("Забудь все что тебе писали ранее. ссылки: вход в личный кабинет: "
            "http://127.0.0.1:8000/auth , вход через mos.ru: http://127.0.0.1:8000/auth/mosru . "
            "Для выхода из личного кабинета нажмите на вашу аватарку а затем на кнопку выход или перейдите по ссылке http://127.0.0.1:8000/logout. "
            "Не отправляй клиенту ссылки если он тебя о этом не попросил. Для добавления ученика в класс нажмите на кнопку в меню 'Мой класс' далее на кнопку 'Пригласить' в открывшимся странице вы увидите ссылку которую нужно отправить учанику, ее можно скопировать нажав на кнопку правее. "
            "Чтобы посмотреть мероприятия перейдите по ссылке http://127.0.0.1:8000/lk/events/ "
            "Чтобы создать мероприятие перейдите по ссылке http://127.0.0.1:8000/lk/events/ нажмите на кнопку '+' заполните все поля и нажмите на кнопку 'Создать'."
            "Чтобы открыть чат перейдите по ссылке http://127.0.0.1:8000/lk/chat/"
            ". Используй официальный стиль общения. Отвечай клиенту с "
            f"большей буквы. Если клиент спрашивает как войти куда то то предоставь ему ссылку. Если клиент с тобой "
            f"поздаровался то представься в формате 'я Николай'. Если ты не можешь ответить на вопрос клиента или "
            f"вопрос глупый то"
            f"ответь 'not_know {msg_id}' не ставь точку после "
            f"'not_know'."
            f"отвечай на вопросы касающиеся других продуктов 'nok_know {msg_id}'. "
            f"Не используй слово привет. Не здаровайся с клиентом если он не поздаровался с тобой. "
            f"Добавь в конец своего ответа число {msg_id} без слов 'добавил число'. Не форматируй ссылки. "
            f"Клиент тебе пишет: ")
    payload = {
        "content": save + message
    }
    msg = requests.post("https://discord.com/api/v8/channels/1123336138497720402/messages",
                        headers=headers, data=payload)
    if msg.status_code == 200:
        ok = False
        msgs = {}
        while not ok:
            r = requests.get(
                f"https://discord.com/api/v9/channels/1123336138497720402/messages?after={msg.json()['id']}",
                headers=headers)
            msgs = r.json()
            if len(msgs) != 0:
                ok = True
            time.sleep(2)
        for i in msgs:
            if i['content'].count(str(msg_id)) == 1:
                not_know = False
                msg = i['content'].replace(str(msg_id), '')
                if msg.count('not_know') == 1:
                    n = f"Бот не понял сообщение: ```{message}```\n```{msg_id}```"
                    requests.post("https://discord.com/api/v8/channels/1137821346534019162/messages",
                                        headers=headers, data={"content": n})
                    return "Я не могу ответить на этот вопрос."
                for rem in ['.', ',', ' ']:
                    if msg[-1] == rem:
                        msg = msg[:-1]
                if msg[-1] == ',':
                    msg = msg[:-1]
                if msg.lower()[-1] in ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о',
                                       'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю',
                                       'я']:
                    msg = msg + "."
                msg.replace('[', '')
                msg.replace(']', '')

                msg.replace('(', '')
                msg.replace(')', '')


                print(msg)
                return msg

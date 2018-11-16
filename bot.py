# -*- coding: utf-8 -*-
import config
import re
import csv
import telebot
from telebot import types
import requests
import json

LINK = "https://search-maps.yandex.ru/v1/?apikey=%s&text=%s&type=biz&lang=ru_RU&ll=%f,%f&spn=0.02,0.02&rspn=1&results=30"
SPN = 0.02

bot = telebot.TeleBot(config.token)

class Bank:
    def __init__(self, bank_id, name, address):
        self.id = bank_id
        self.name = name
        self.address = address
        self.queue = []

    def append_user(self, user):
        self.queue.append(user)
        return self.queue

    def info(self):
        rtn_str = str(self.id) + "\n" + self.name + "\n" + self.address + "\n[" 
        for u in self.queue:
            rtn_str = rtn_str + "%d\n" % (u.id)
        rtn_str = rtn_str + "]"
        return rtn_str

    def to_json(self):
        obj = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
        }
        users = []
        for u in self.queue:
            users.append(u.to_json())
        obj["queue"] = users
        return obj



class User:
    def __init__(self, user_id=None, name=None, location=None, query=None, queue_number=None, bank_id=None):
        self.id = user_id
        self.name = name
        self.location = location
        self.query = query
        self.queue_number = queue_number
        self.bank_id = bank_id

    def assign_user_id(self, user_id):
        self.id = user_id

    def assign_name(self, name):
        self.name = name
    
    def assign_query(self, query):
        self.query = query

    def assign_location(self, location):
        self.location = location

    def assign_queue_number(self, queue_number):
        self.queue_number = queue_number

    def assign_bank_id(self, bank_id):
        self.bank_id = bank_id

    def info(self):
        rtn_str = str(self.id) + "\n" + self.name + "\n" + self.query + "\n" + "%s, %s" % (self.location.longitude, self.location.latitude) + "\n" + str(self.queue_number) + "\n" + str(self.bank_id) + "\n"
        return rtn_str

    def to_json(self):
        print(self.location)
        return {
            "id": self.id,
            "name": self.name,
            "location":{
                "latitude": self.location['latitude'] if type(self.location) is type({}) else self.location.latitude,
                "longitude": self.location['longitude'] if type(self.location) is type({}) else self.location.longitude,
            },
            "query": self.query,
            "queue_number": self.queue_number,
            "bank_id": self.bank_id,
        }

user = User()
banks = {}
global user_banks
user_banks = []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Здравствуйте! Пожалуйста, отправьте ваше местоположение.")

@bot.message_handler(content_types=['location'])
def get_location(message):
    init_location(message)

@bot.message_handler(commands=['bank'])
def get_bank(message):
    init_query(message)

@bot.message_handler(commands=['choose'])
def get_choice(message):
    update_queue(message)

@bot.message_handler(commands=['queue'])
def get_queue(message):
    show_queue(message)

@bot.message_handler(commands=['all_queues'])
def get_all_queues(message):
    show_all_queues(message)

@bot.message_handler(commands=['done'])
def delete_queue(message):
    delete_user(message)

def delete_user(message):
    if user is None:
        bot.reply_to(message, "Начните заново.")
    elif user.queue_number is None or user.bank_id is None:
        bot.reply_to(message, "Начните заново.")
    elif len(banks) == 0 or len(banks[user.bank_id].queue) == 0:
        bot.reply_to(message, "Начните заново.")
    
    print(banks[user.bank_id].queue)
    print(user.info())
    idx = banks[user.bank_id].queue.index(user)
    print(idx)
    del banks[user.bank_id].queue[idx]
    bot.reply_to(message, "До свидания. Хорошего дня!")

def show_all_queues(message):
    banks = from_csv()
    str_all = ""
    for bank_id in banks:
        bank = banks[bank_id]
        name = banks[bank_id].name
        address = banks[bank_id].address
        rtn_str = name + ", " + address + "\n"
        for u in banks[bank_id].queue:
            rtn_str = rtn_str + u.name + ": " + str(u.queue_number) + "\n"
        rtn_str = rtn_str + "\n"
        str_all = str_all + rtn_str
    bot.reply_to(message, str_all)


def show_queue(message):
    banks = from_csv()
    queue_len = ""
    print(user)
    print(banks[user.bank_id].queue)
    name = banks[user.bank_id].name
    address = banks[user.bank_id].address
    for queue_user in banks[user.bank_id].queue:
        queue_len = queue_len + queue_user.name + ", " + str(queue_user.queue_number) + "\n"

    if queue_len == "":
        bot.reply_to(message, "Очередь пуста.")
        return
    bot.reply_to(message, name + ", " + address + "\n" + queue_len)

def from_csv():
    with open('database.json') as infile:
        data = json.load(infile)
        banks = {}
        for bank_id in data:
            bank = data[bank_id]
            name = bank["name"]
            address = bank["address"]
            new_bank = Bank(bank_id=bank_id, name=name, address=address)
            for u in bank["queue"]:
                name = u["name"]
                user_id = int(u["id"])
                queue_number = u["queue_number"]
                bank_id = u["bank_id"]
                query = u["query"]
                location = {'latitude': u["location"]["latitude"], 'longitude': u["location"]["longitude"]}
                new_user = User(user_id=user_id, name=name, location=location, query=query, queue_number=queue_number, bank_id=bank_id)
                new_bank.queue.append(new_user)
            banks[bank_id] = new_bank
        return banks

def to_csv(banks):
    print(banks)
    obj = {}
    for bank_id in banks:
        bank = banks[bank_id]
        obj[bank_id] = bank.to_json()
    with open('database.json', 'w') as outfile:
        json.dump(obj, outfile)



def update_queue(message):
    banks = from_csv()
    text = message.json["text"][8:]
    print(text.encode('utf-8'))
    print(user_banks)
    print("len user_banks %d" % (len(user_banks)))

    user.assign_bank_id(bank_id=user_banks[int(text) - 1].id)
    ln = len(banks[user.bank_id].queue)
    user.assign_queue_number(queue_number=ln)
    banks[user.bank_id].append_user(user=user)
    print(type(user.bank_id))
    print(banks)
    to_csv(banks)
    bot.reply_to(message, "Ваш номер: %d. Текущую очередь в вашем банке можно посмотреть по команде /queue." % (ln))


def init_location(message):
    # banks = from_csv()
    username = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    user_id = message.chat.id
    location = message.location
    user.assign_user_id(user_id=user_id)
    user.assign_name(name=username + " " + first_name + " " + last_name)
    user.assign_location(location=location)
    print(user.location)
    bot.reply_to(message, "Ваше местоположение установлено. Пожалуйста, напишите название банка с командой /bank.")


def init_query(message):
    # banks = from_csv()
    print(user.location)
    text = message.json["text"][6:]
    print(text.encode('utf-8'))
    user.assign_query(text)
    make_request(message)

def make_request(message):
    banks = from_csv()
    r = requests.get(LINK % (config.apikey, user.query, user.location.longitude, user.location.latitude))
    # print(r)
    # print(r.content)
    content = json.loads(r.content)
    search_response = content["properties"]["ResponseMetaData"]["SearchResponse"]
    cnt_banks = search_response["found"]
    if cnt_banks == 0:
        bot.reply_to(message, "К сожалению, поблизости от вас не найдено банков.")
        return
    banks_response = content["features"]
    global user_banks
    user_banks = []
    for bank in banks_response:
        bank_info = bank["properties"]["CompanyMetaData"]
        bank_id = bank_info["id"]
        if banks.get(bank_id) is not None:
            user_banks.append(banks[bank_id])
            continue
        print(type(bank_id))
        bank_address = bank_info["address"]
        bank_name = bank_info["name"]
        new_bank = Bank(bank_id=bank_id, name=bank_name, address=bank_address)
        banks[bank_id] = new_bank
        user_banks.append(new_bank)

    print(user.location)
    to_csv(banks=banks)

    print("len banks_response %d" % (len(banks_response)))
    print("len user_banks %d" % (len(user_banks)))
    ans = "Количество банков вблизи: " + str(cnt_banks)
    str_banks = ""
    cnt = 0
    for bank in user_banks:
        cnt = cnt + 1
        bank_name = bank.name
        bank_address = bank.address
        str_banks = str_banks + str(cnt) + ") " + "\"" + bank_name.encode('utf-8') + "\", " + bank_address.encode('utf-8') + "\n"

    print("len user_banks %d" % (len(user_banks)))
    bot.reply_to(message, ans + "\n" + str_banks + "\n" + "Пожалуйста, отправьте номер отделения с командой /choose.")


bot.polling(none_stop = True, interval = 0)
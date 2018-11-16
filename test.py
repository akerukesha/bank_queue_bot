# -*- coding: utf-8 -*-
import requests
import re
# params = {"languagecode": "en", "city_ids": [34]}
# r = requests.get("https://distribution-xml.booking.com/json/bookings.getHotels", auth=("b_women_tech17", "uEt9aQ,.3KNq&vfa&Cx8"), params=params)
# # hotel_params = {"languagecode": "en", "hotel_ids": hotel_ids}
# # q = requests.get("https://distribution-xml.booking.com/json/bookings.getHotels", auth=("b_women_tech17", "uEt9aQ,.3KNq&vfa&Cx8"), params=hotel_params)
# print(r.content)

print(re.search(r"[0-9]*", "13").group())

class User:
    def __init__(self):
        self.id = None
        self.name = None
        self.location = None
        self.query = None
        self.queue_number = None
        self.bank_id = None
        self.banks = []

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

    def assign_banks(self, banks):
        self.banks = banks

    def info(self):
        rtn_str = str(self.id) + "\n" + self.name + "\n" + self.query + "\n" + "%s, %s" % (self.location.longitude, self.location.latitude) + "\n" + str(self.queue_number) + "\n" + str(self.bank_id) + "\n["
        for bank in self.banks:
            rtn_str = rtn_str + bank.info() + "\n"
        rtn_str = rtn_str + "]"
        return rtn_str

user = User()
u = User()
if user is u and user == u:
	print("bad")
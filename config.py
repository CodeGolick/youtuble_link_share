# - *- coding: utf- 8 - *-
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
BOT_TOKEN = config["settings"]["token"]
admins = config["settings"]["admin_id"]
max_per_day = int(config['settings']['max_per_day'])
if "," in admins:
    adminList = admins.split(",")
    n = []

    for each in adminList:
        n.append(int(each))
    adminList = n
else:
    if len(admins) >= 1:
        adminList = [int(admins)]
    else:
        adminList = []
        print("***** Вы не указали админ ID *****")

max_cc_per_msg = 50
knownUsers = {} 
userStep = {}
username_list = {}
data_transfer_dict = {}

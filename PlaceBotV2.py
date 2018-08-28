# -*- coding: utf-8 -*-

import telepot
import telegram
import requests
import json
import webbrowser
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

bot = telepot.Bot("<TOKEN>")
categoria = None

def btnStart():
    list_buttons = [
        [
            KeyboardButton(text = "Começar")
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard = list_buttons, resize_keyboard = True, one_time_keyboard = True)

    return reply_markup

def btnEscolherEstabelecimento():
    list_buttons = [
        [
            KeyboardButton(text = "Ensino Médio"),
            KeyboardButton(text = "Ensino Fundamental"),
            KeyboardButton(text = "Universidade"),
            KeyboardButton(text = "Teatro")
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard = list_buttons, resize_keyboard = True, one_time_keyboard = True)

    return reply_markup

def btnEnviarLocalizacao():
    list_buttons = [
        [
            KeyboardButton(text = "Enviar Localização", request_location = True)
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard = list_buttons, resize_keyboard = True, one_time_keyboard = True)

    return reply_markup

def btnEscolherDestino(locais):
    list_buttons = [
        [
            KeyboardButton(text = locais[str(0)][0]),
            KeyboardButton(text = locais[str(1)][0]),
            KeyboardButton(text = locais[str(2)][0])
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard = list_buttons, resize_keyboard = True, one_time_keyboard = True)

    return reply_markup

def mandaLocais(userID, x, data):
    bot.sendMessage(userID, data['response']['groups'][0]['items'][x]['venue']['name'].encode(encoding='UTF-8', errors='strict'))
    
    if data['response']['groups'][0]['items'][x]['venue']['location']:
        if data['response']['groups'][0]['items'][x]['venue']['location']['formattedAddress']:
            for y in range(0, len(data['response']['groups'][0]['items'][x]['venue']['location']['formattedAddress'])):
                bot.sendMessage(userID, data['response']['groups'][0]['items'][x]['venue']['location']['formattedAddress'][y].encode(encoding='UTF-8', errors='strict'))

    bot.sendMessage(userID, '------')

def rotas(local, latUser, lonUser, userID):
    latLocal = local[1]
    lonLocal = local[2]

    url = "https://www.google.com/maps/dir/" + str(latUser) + ',' + str(lonUser) + '/' + str(latLocal) + ',' + str(lonLocal)

    bot.sendMessage(userID, "Rota: " + url)

def localiza(message):
    tipoMsg, tipoChat, userID = telepot.glance(message)
    global categoria
    global latUser
    global lonUser
    limitePesquisa = 3
    temlocal = True
    if tipoMsg == "text":
        if message['text'] == "/start":
            bot.sendMessage(userID, "Bem vindo")
            reply_markup = btnEscolherEstabelecimento()
            bot.sendMessage(userID, "O que procura?", reply_markup = reply_markup)
        elif message['text'] == "Ensino Médio":
            categoria = "high school"
        elif message['text'] == "Ensino Fundamental":
            categoria = "elementary school"
        elif message['text'] == "Universidade":
            categoria = 'universidade'
        elif message['text'] == "Teatro":
            categoria = 'theater'
        if temlocal:
            for x in locais.keys():
                if message['text'] == locais[str(x)][0]:
                    local = locais[str(x)]
                    rotas(local, latUser, lonUser, userID)
                    reply_markup = btnStart()
                    bot.sendMessage(userID, "Aperte 'Começar' para iniciar uma nova pesquisa!", reply_markup = reply_markup)
                    categoria = ''
        if message['text'] == "Começar":
            message['text'] = "/start"
            localiza(message)
        if categoria == "high school" or categoria == 'elementary school' or categoria == 'universidade' or categoria == 'theater':
            reply_markup = btnEnviarLocalizacao()
            bot.sendMessage(userID, "Me envie sua localização. Por favor, ative o GPS", reply_markup = reply_markup)

    if tipoMsg == "location":
        latUser = message['location']['latitude']
        lonUser = message['location']['longitude']
        latlon = str(latUser) + ',' + str(lonUser)
        api_url = "https://api.foursquare.com/v2/venues/explore"
        params = {'client_id' : 'WJCBZKPRLMVOR51PALKM3JOUH2EKTW154YHXGGTKLGWLCH01',
                  'client_secret' : 'CAKZAZQIPOKGPGZOCNTMMPLBAUBHDS4K5PBBHPCVYLGLMMO2',
                  'v' : '20120609',
                  'll' : latlon,
                  'radius' : 30000,
                  'query' : categoria,
                  'limit' : limitePesquisa}
        categoria = ""
        resp = requests.get(api_url, params)
        data = json.loads(resp.text)
        temlocal = True
        if data['response']['groups'][0]['items']:
            for x in range(0, limitePesquisa):
                mandaLocais(userID, x, data)
                nome = data['response']['groups'][0]['items'][x]['venue']['name']
                latDestino = data['response']['groups'][0]['items'][x]['venue']['location']['lat']
                lonDestino = data['response']['groups'][0]['items'][x]['venue']['location']['lng']
                locais[str(x)] = str(nome), latDestino, lonDestino
        else:
            bot.sendMessage(userID, "Não há locais perto de você! Sinto muito.")
            temlocal = False
        if temlocal:
            reply_markup = btnEscolherDestino(locais)
            bot.sendMessage(userID, "Escolha o destino para traçar uma rota", reply_markup = reply_markup)
        else:
            reply_markup = btnStart()
            bot.sendMessage(userID, "Aperte 'Começar' para iniciar uma nova pesquisa!", reply_markup = reply_markup)

locais = {}
bot.message_loop(localiza)
while True:
    pass

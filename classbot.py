#!pip install telebot
#!pip install https://huggingface.co/latincy/la_core_web_lg/resolve/main/la_core_web_lg-any-py3-none-any.whl
#!pip install googletrans==3.1.0a0

import telebot
from telebot import types
import spacy
from spacy.morphology import Morphology
from googletrans import Translator

# Создаем переводчик
translator = Translator()

# Задаем исходные язык и целевой язык
src = 'la'
dest = 'ru'

nlp = spacy.load('la_core_web_lg')

bot = telebot.TeleBot('6725473706:AAHeymN9rL2t2YGLwNTfxDQa6f8NI6AKzqA')

#классы

#имена
class Noun:
    def __init__(self, token, lemma, trans_form, trans_lemma, case, gender, number):
        self.token = token
        self.lemma = lemma
        self.trans_form = trans_form
        self.trans_lemma = trans_lemma
        self.case = case
        self.gender = gender
        self.number = number

    def get_full_info(self):
        """Информация о слове"""
        info = f"'{self.token} - {self.trans_form}. Инфо: {self.lemma} - {self.trans_lemma}, case={self.case}, gender={self.gender}, number={self.number}"
        return info.title()


#глагольные формы
class Verb:
    def __init__(self, token, lemma, trans_form, trans_lemma, mood, number, person, tense, verbform,  voice):
        self.token = token
        self.lemma = lemma
        self.trans_form = trans_form
        self.trans_lemma = trans_lemma
        self.mood = mood
        self.number = number
        self.person = person
        self.tense = tense
        self.verbform = verbform
        self.voice = voice

    def get_full_info(self):
        """Информация о слове"""
        info = f"'{self.token} - {self.trans_form}. Инфо: {self.lemma} - {self.trans_lemma}, mood = {self.mood}, person = {self.person}, number = {self.number}, tense = {self.tense}, verbform = {self.verbform}, voice = {self.voice}"
        return info.title()




#неизменяемые части речи + пунктуация
class Conj:
    def __init__(self, token, lemma, trans_form, trans_lemma):
        self.token = token
        self.lemma = lemma
        self.trans_form = trans_form
        self.trans_lemma = trans_lemma

    def get_full_info(self):
        """Информация о слове"""
        info = f"'{self.token} - {self.trans_form}. Инфо: {self.lemma} - {self.trans_lemma}"
        return info.title()


class Adv:
    def __init__(self, token, lemma, trans_form, trans_lemma):
        self.token = token
        self.lemma = lemma
        self.trans_form = trans_form
        self.trans_lemma = trans_lemma

    def get_full_info(self):
        """Информация о слове"""
        info = f"'{self.token} - {self.trans_form}. Инфо: {self.lemma} - {self.trans_lemma}"
        return info.title()


class Punct:
    def __init__(self, punct):
        self.punct = punct


# функции бота

# 0
def obrabotka(a):
  l = a.split(', ')
  l[-1] = l[-1].replace('|', '=')
  s = l[-1].split('=')
  s = s[1::2]
  l[-1] = s
  return l


# 1 -- создание списка из списков с word properties
def normal_form(doc):
  normal = []
  for i in range(len(doc)):
    if doc[i].pos_ == 'PUNCT':
      normal.append([i+1, doc[i].text, 'PUNCT'])

    else:
      trans_form = translator.translate(doc[i].text, src=src, dest=dest).text
      trans_lem = translator.translate(doc[i].lemma_, src=src, dest=dest).text

      if (doc[i].pos_ != 'CCONJ') and (doc[i].pos_ != 'ADV'):
        k = obrabotka(f'{i+1}, {doc[i].text}, {doc[i].lemma_}, {trans_form}, {trans_lem}, {doc[i].pos_},  {doc[i].morph}')
        normal.append(k)

      else:
        normal.append([i+1, doc[i].lemma_, trans_lem, doc[i].pos_])
  print(normal)
  return normal

# Вывод финального разбора
def razbor1(doc):
  razbor = ""
  for i in range(len(doc)):
    if doc[i].pos_ != 'PUNCT':
      forma = doc[i].text
      lem = doc[i].lemma_
      razbor += (f'{doc[i].text},  {doc[i].lemma_},  {doc[i].pos_},  {doc[i].morph}')
      perevform = translator.translate(forma, src=src, dest=dest).text
      perevlem = translator.translate(lem, src=src, dest=dest).text
      razbor += f'\nЛемма - *{perevlem}*. Предполагаемый перевод формы - *{perevform}*.\n'
  return razbor


#2 -- присвоение классов
def classification(a):
    if a[2] == 'PUNCT':
        a[0] = Punct(a[1], 'punct')
        return print(f"{a[0].lemma}")

    if (a[5] == 'NOUN') or (a[5] == 'PROPN') or (a[5] == 'ADJ') or (a[5] == 'PRON'):
        a[0] = Noun(a[1], a[2], a[3], a[4], *[i for i in a[6]])
        return print(f"{a[0].lemma}")

    if a[5] == 'VERB':
        a[0] = Verb(a[1], a[2], a[3], a[4], *[i for i in a[6]])
        return print(f"{a[0].lemma}")

    if a[5] == 'CCONJ':
        a[0] = Conj(a[1], 'translation')
        return print(f"{a[0].lemma}")

    if a[5] == 'ADJ':
        a[0] = Adv(a[1], 'translation')
        return print(f"{a[0].lemma}")



#3 -- вывод результата
def resultat(normal):
  print(normal)
  result = ''
  for i in normal:
    print(classification(i))
    #print(i[0].get_full_info())
    result += i[0].get_full_info() + '\n'
    print(result)
  return result

#бот

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    pressStartButton = 'Кнопка старт'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    latinButton = types.KeyboardButton('ЛАТЫНЬ')
    markup.add(latinButton)

    bot.send_message(message.chat.id, "Напишите своё предложение на латыни!",
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.chat.type == 'private':
        if message.text == 'ЛАТЫНЬ':
            bot.send_message(message.chat.id, 'Можете написать слово, словосочетание или предложение на латыни, а мы постараемся его перевести.')
        else:
            user_id = message.from_user.id
            doc = nlp(message.text)

            perevtext = translator.translate(doc, src=src, dest=dest).text



            bot.send_message(message.chat.id, "Сначала вы увидите перевод всего предложения, а потом пословный морфологический разбор и предполагаемые переводы леммы и формы слова в предложении. \n"
                             + "\nПредполагаемый перевод от Google Translate: \n" + f"*{perevtext}*" + "\n \n" + resultat(normal_form(doc)), parse_mode="Markdown")


bot.polling(none_stop=True)

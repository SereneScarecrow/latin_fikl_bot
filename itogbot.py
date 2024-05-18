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
    def __init__(self, token, lemma, trans_form, trans_lemma, POS, pad='Unknown', gender='None', number='None'):
        self.POS = POS
        self.token = token
        self.lemma = lemma
        self.trans_form = trans_form
        self.trans_lemma = trans_lemma
        self.pad = pad
        self.gender = gender
        self.number = number

    def get_full_info(self):
        """Информация о слове"""
        info = f"*{self.token}* - _{self.trans_form}_. \n    ‧ {self.lemma} - {self.trans_lemma}. {self.POS} \n    ‧ {self.pad}, {self.gender} {self.number}"
        return info.title()


#глагольные формы
class Verb:
    def __init__(self, token, lemma, trans_form, trans_lemma, POS, mood='None', number='None', person=0, tense='Unknown', verbform='None',  voice='None'):
        self.POS = POS
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
        info = f"*{self.token}* - _{self.trans_form}_. \n    ‧ {self.lemma} - {self.trans_lemma}. {self.POS} \n    ‧ {self.mood} {self.person}{self.number}, {self.tense} {self.verbform} {self.voice}"
        return info.title()

#неизменяемые части речи + пунктуация
class Conj:
    def __init__(self, lemma, trans_lemma, POS):
        self.POS = POS
        self.lemma = lemma
        self.trans_lemma = trans_lemma

    def get_full_info(self):
        """Информация о слове"""
        info = f"*{self.lemma}* - _{self.trans_lemma}_. {self.POS}"
        return info.title()


class Non_change:
    def __init__(self, lemma, trans_lemma, POS):
        self.POS = POS
        self.lemma = lemma
        self.trans_lemma = trans_lemma

    def get_full_info(self):
        """Информация о слове"""
        info = f"*{self.lemma}* - _{self.trans_lemma}_. {self.POS}"
        return info.title()


class Punct:
    def __init__(self, punct, POS):
        self.POS = POS
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

#NOUN, ADJ, PROPN, PRON, DET -- a[5], len(a) == 7 (i, token, lemma, translated token, translated lemma, POS, [morph])
#CCONJ, SCONJ, ADV, NUM -- a[3], len(a) == 5 (i, lemma, translated lemma, POS)
#PUNCT -- a[2], len(a) == 3 (i, punct)

def normal_form(doc):
    normal = []
    for i in range(len(doc)):
      if doc[i].pos_ == 'PUNCT':
        normal.append([i+1, doc[i].text, 'PUNCT'])

      else:
        trans_form = translator.translate(doc[i].text, src=src, dest=dest).text
        trans_lem = translator.translate(doc[i].lemma_, src=src, dest=dest).text

        if (doc[i].pos_ != 'CCONJ') and (doc[i].pos_ != 'ADV')and (doc[i].pos_ != 'SCONJ') and (doc[i].pos_ != 'ADP') and (doc[i].pos_ != 'PART') and (doc[i].pos_ != 'NUM'):
          k = obrabotka(f'{i+1}, {doc[i].text}, {doc[i].lemma_}, {trans_form}, {trans_lem}, {doc[i].pos_},  {doc[i].morph}')
          normal.append(k)

        else:
          normal.append([i+1, doc[i].lemma_, trans_lem, doc[i].pos_])
    #print(normal)
    return normal

#2 -- присвоение классов
def classification(a):
    if a[2] == 'PUNCT':
        a[0] = Punct(a[1], a[2])
        return True

    if (a[3] == 'CCONJ') or (a[3] == 'SCONJ'):
        a[0] = Conj(a[1], a[2], a[3])
        return True

    if (a[3] == 'ADV') or (a[3] == 'ADP') or (a[3] == 'PART') or (a[3] == 'NUM'):
        a[0] = Non_change(a[1], a[2], a[3])
        return True

    if (a[5] == 'NOUN') or (a[5] == 'PROPN') or (a[5] == 'ADJ') or (a[5] == 'PRON') or (a[5] == 'DET'):
        a[0] = Noun(a[1], a[2], a[3], a[4], a[5], *[i for i in a[6]])
        return True

    if (a[5] == 'VERB') or (a[5] == 'AUX'):
        a[0] = Verb(a[1], a[2], a[3], a[4], a[5], *[i for i in a[6]])
        return True



#3 -- вывод результата
def resultat(normal):
  #print(normal)
  result = ''
  for i in normal:
    classification(i)
    #print(i[0].get_full_info())
    if i[0].POS != "PUNCT":
      result += i[0].get_full_info() + '\n'
      #print(result)
  return result

#4 -- поиск конструкций

#accusativus duplex

def acc_du(a):
    s = ''
    acc_constr = []
    for i in range(len(a)-1):
        if a[i][0].__class__.__name__ == 'Noun' and a[i+1][0].__class__.__name__ == 'Noun':
            if a[i][0].pad == 'Acc' and a[i+1][0].pad == 'Acc':
                if a[i][0].number == a[i+1][0].number:
                    s = a[i][0].token + ' ' + a[i+1][0].token
                    acc_constr.append(s)
                    s = ''
    return acc_constr

#nominativus duplex

def nom_du(a):
    s = ''
    nom_constr = []
    for i in range(len(a)-1):
        if a[i][0].__class__.__name__ == 'Noun' and a[i+1][0].__class__.__name__ == 'Noun':
            if a[i][0].pad == 'Nom' and a[i+1][0].pad == 'Nom':
                if a[i][0].number == a[i+1][0].number and a[i][0].gender == a[i+1][0].gender:
                    s = a[i][0].token + ' ' + a[i+1][0].token
                    nom_constr.append(s)
                    s = ''
    return nom_constr

#accusativus cum infinitivo

def acc_inf(a):
    s = ''
    acc_inf_constr = []
    for i in range(len(a)-1):
        for j in range(len(a)):
            if a[i][0].__class__.__name__ == 'Verb':
                if a[i][0].POS == 'VERB' and a[i][0].mood == 'Inf' and a[i][0].voice == 'Act':
                    if a[j][0].__class__.__name__ == 'Noun' and a[j][0].pad == 'Acc':
                        if a[i][0].number == a[j][0].number:
                            s = a[i][0].token + ' ' + a[j][0].token
                            acc_inf_constr.append(s)
                            s = ''
                if a[i][0].POS == 'AUX':
                    if a[j][0].__class__.__name__ == 'Noun' and a[j][0].pad == 'Acc':
                        s = a[i][0].token + ' ' + a[j][0].token
                        acc_inf_constr.append(s)
                        s = ''
    return acc_inf_constr

#nominativus cum infinitivo

def nom_inf(a):
    s = ''
    nom_inf_constr = []
    for i in range(len(a)-1):
        for j in range(len(a)):
            if a[i][0].__class__.__name__ == 'Verb':
                if a[i][0].POS == 'VERB' and a[i][0].mood == 'Inf' and a[i][0].voice == 'Pas':
                    if a[j][0].__class__.__name__ == 'Noun' and a[j][0].pad == 'Nom':
                        if a[i][0].number == a[j][0].number:
                            s = a[i][0].token + ' ' + a[j][0].token
                            nom_inf_constr.append(s)
                            s = ''
                if a[i][0].POS == 'AUX':
                    if a[j][0].__class__.__name__ == 'Noun' and a[j][0].pad == 'Nom':
                        s = a[i][0].token + ' ' + a[j][0].token
                        nom_inf_constr.append(s)
                        s = ''
    return nom_inf_constr

#5 -- вывод конструкций

def constr(normal):
  itog = ""
  accd = acc_du(normal)
  nomd = nom_du(normal)
  accinf = acc_inf(normal)
  nominf = nom_inf(normal)
  if len(accd) > 0:
    itog += "*Accusativus Duplex:* " + ("; ").join(accd) + "\n"
  if len(nomd) > 0:
    itog += "*Nominativus Duplex:* " + ("; ").join(nomd) + "\n"
  if len(accinf) > 0:
    itog += "*Accusativus cum infinitivo:* " + ("; ").join(accinf) + "\n"
  if len(nominf) > 0:
    itog += "*Nominativus cum infinitivo:* " + ("; ").join(nominf) + "\n"

  return itog

#бот

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    pressStartButton = 'Кнопка старт'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    latinButton = types.KeyboardButton('ЛАТЫНЬ')
    spravkaButton = types.KeyboardButton('СПРАВОЧНИК')
    markup.add(latinButton, spravkaButton)

    bot.send_message(message.chat.id, "Напишите своё предложение на латыни!",
                     parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.chat.type == 'private':
        if message.text == 'ЛАТЫНЬ':
            bot.send_message(message.chat.id, 'Можете написать слово, словосочетание или предложение на латыни, а мы постараемся его перевести. Если вы пишете слишком длинный текст, бот может не вывести вам результат.')
        elif message.text == 'СПРАВОЧНИК':
            bot.send_message(message.chat.id, '__Справка по используемым конструкциям и как их переводить.__ \n \n'
                             + '*Accusativus duplex (Двойной винительный)*\n    глагол + два имени в аккузативе\n    перевод: глагол + имя в аккузативе + имя в инструменталисе'
                             + '\n \n    _Homer-um poet-am clar-um puta-mus\n    Гомера поэта знаменитого мы считаем (досл.)\n    Мы считаем Гомера знаменитым поэтом_'
                             + '\n \n \n*Nominativus duplex (Двойной именительный)*\n    аналогичен Acc. duplex \n    — [глагол в страдательном залоге] + два имени в номинативе\n    перевод: глагол + имя в номинативе + имя в инструменталисе'
                             + '\n \n    _Homerus poeta clarus puta-tur\n    Гомер поэт знаменитый считается (досл.)\n    Гомер считается знаменитым поэтом_'
                             + '\n \n \n*Accusativus cum infinitivo (Винительный и инфинитив)*\n    — глагол + [сущ/мест в аккузативе + инфинитив]\n' + '    перевод: глагол + [придаточное предложение с союзом что/чтобы/как]\n \n'
                             + '    _Trad-unt Homer-um caec-um fuisse\n    Передают Гомера слепого быть (досл.)\n    Говорят, что Гомер был слепым_\n'
                             + '\n \n*Nominativus cum infinitivo (Именительный с инфинитивом)*\n    аналогичен Acc. cum inf.\n    — глагол в стр. залоге + [имя в номинативе + инфинитив]' + '\n    перевод: глагол + [придаточное изъяснительное с предлогом что/чтобы/как]' + '\n \n'
                             + '    _Homer-us caec-us fuisse traditur\n    Гомер слепой быть передаётся (досл.)\n    Говорится, что Гомер был слепым_\n \n'
                             + '_Все эти конструкции употребляются с  управляющим глаголом типа называть, считать, описывать и так далее._', parse_mode="Markdown")
        else:
            user_id = message.from_user.id
            s = message.text
            s = s.replace("  ", " ")
            doc = nlp(s)

            perevtext = translator.translate(doc, src=src, dest=dest).text

            normal = normal_form(doc)
            bot.send_message(message.chat.id, "Предполагаемый перевод от Google Translate: \n" + f"*{perevtext}*"
                             + "\n \n" + resultat(normal) + "\n \nВозможные конструкции в тексте:\n \n" + constr(normal), parse_mode="Markdown")


bot.polling(none_stop=True)

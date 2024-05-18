# latin_fikl_bot

Список участников:

Жигулина Александра;
Шумакова Александра;
Гурова Ульяна;
Гуськова Анна.

Описание проекта:

Бот, который принимает от пользователя слово/словосочетание/предложение на латинском языке 
и выводит сначала перевод всей введённый фразы,
а затем определяет все частеречные принадлежности, формы и переводы каждого слова в отдельности, 
а также найдены потенциальные грамматические конструкции латинского языка

Конструкции:

- Аккузатив двойной;

- Номинатив двойной;

- Аккузатив с инфинитивом;

- Номинатив с инфинитивом.


Структура репозитория:

main -- работающий код бота, документация


bot_code (более или менее работающие версии бота с разной начинкой):


- almost_working_verion_latin_bot, bot1, bot_2_with translation, bot_latin translator
classbot.py, googletranslator, working_latin_bot -- рабочие версии кода бота

- itogbot.py -- финальный бот, также есть в main

latin_constr (анализ конструкций и классы по частям речи):

- acc_cum_inf, acc_nom_duplex

- classes



Как запустить код: 
1) из main скачать/скопировать код bot.py
2) вставить его в гугл коллаб
3) убрать # перед pip install
4) жмакнуть на кнопочку запустить
5) вуаля, вы превосходны


Ссылки на ресурсы, откуда был взят код:
https://habr.com/ru/articles/659329/ -- изначальный код тг бота

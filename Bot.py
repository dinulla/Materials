import telebot
import os
from os import listdir
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = '6088757820:AAHE5VQZVpXTljW04vYx-ZnLjj8AxXvwlT0'

directory = 'C:\\Учеба\\Цифровые кафедры\\LabsBot\\Data'


bot = telebot.TeleBot(TOKEN)

dirs = [dir[0].split('\\')[-1] for dir in os.walk(directory)]
dirs.pop(0)


def get_lab_list(files):
    labs = []
    for file in files:
        labCode = file.split('_')[1].split('.')[0]
        if labCode not in labs:
            labs.append(labCode)

    return labs


def lab_markup(dirId):
    dir = directory + "\\" + dirs[dirId]
    files = [file for file in listdir(dir)]

    labs = get_lab_list(files)

    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton(labs[0], callback_data="lab_" + str(dirId) + "_" + labs[0]))
    for i in range(1, len(labs)):
        markup.keyboard[0].append(InlineKeyboardButton(labs[i], callback_data="lab_" + str(dirId) + "_" + labs[i]))
    return markup


def file_markup(dirId, lab):
    dir = directory + "\\" + dirs[dirId]
    files = [file for file in listdir(dir) if lab in file]

    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton(files[0].split('_')[1], callback_data="file_" + str(dirId) + "_" + files[0]))
    for i in range(1, len(files)):
        markup.keyboard[0].append(
            InlineKeyboardButton(files[i].split('_')[1], callback_data="file_" + str(dirId) + "_" + files[i]))
    return markup


def upl_dirs_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton(dirs[0], callback_data="upl_dir" + str(0)))
    for i in range(1, len(dirs)):
        markup.keyboard[0].append(InlineKeyboardButton(dirs[i], callback_data="upl_dir" + str(i)))
    return markup


def dwn_dirs_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton(dirs[0], callback_data="dwn_dir" + str(0)))
    for i in range(1, len(dirs)):
        markup.keyboard[0].append(InlineKeyboardButton(dirs[i], callback_data="dwn_dir" + str(i)))
    return markup


def menu_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Загрузить работу", callback_data="btn_upload"),
               InlineKeyboardButton("Скачать работу", callback_data="btn_download"))

    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "btn_upload":
        bot.send_message(call.from_user.id, "Выбери раздел физики, к которому относится твоя лаба.",
                         reply_markup=upl_dirs_markup())

    elif call.data == "btn_download":
        bot.send_message(call.from_user.id, "Выбери раздел физики, который тебя интересует.",
                         reply_markup=dwn_dirs_markup())

    elif "upl_dir" in call.data:
        dirId = int(call.data.replace("upl_dir", ''))
        curDir = directory + "\\" + dirs[dirId]
        msg = bot.reply_to(call.message,
                           "Добавь файл. Название файла должно состоять из трехзначного кода лабы +.pdf (если код меньше ста, то необходимо добавить нули для получения трехзначного, например, 001.pdf)")
        bot.register_next_step_handler(msg, save_file, [curDir])


    elif "dwn_dir" in call.data:
        dirId = int(call.data.replace("dwn_dir", ''))
        bot.send_message(call.from_user.id, """Выбери нужную работу из списка. \n
Если работы не нашлось, то придется самому сделать лабу. Но потом ты можешь выгрузить сюда, чтобы помочь остальным товарищам.""",
                         reply_markup=lab_markup(dirId))

    elif "lab_" in call.data:
        fileDir = call.data.replace("lab_", '').split('_')
        bot.send_message(call.from_user.id, """Выбери любой файл, скачать можно каждый.""",
                         reply_markup=file_markup(int(fileDir[0]), fileDir[1]))


    elif "file_" in call.data:
        fileDir = call.data.replace("file_", '').split('_')

        f = open(directory + "\\" + dirs[int(fileDir[0])] + "\\" + fileDir[1] + "_" + fileDir[2], 'rb')
        bot.send_document(call.from_user.id, f, visible_file_name=fileDir[2])


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id,
                     'Привет, этот бот создан для облегчения твоей жизни на физфаке. С помощью него ты можешь найти нужную тебе лабораторную работу, а также помочь другим ребятам, выгрузив свою лабу.')
    bot.send_message(message.from_user.id, 'Выбери раздел, который тебя интересует.', reply_markup=menu_markup())


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.from_user.id, """
/start - Начало работы с ботом.
/info - Информация о боте.""")


def save_file(message, dir):
    try:
        fileName = message.document.file_name
        if fileName.split('.')[0].isdigit() and len(fileName.split('.')[0]) == 3:
            fileInfo = bot.get_file(message.document.file_id)
            downloadedFile = bot.download_file(fileInfo.file_path)
            with open(dir[0] + "\\" + str(message.from_user.id) + "_" + fileName, 'wb') as newFile:
                newFile.write(downloadedFile)

            bot.reply_to(message, 'Файл был добавлен! Большое спасибо от всех, кому она пригодится!')
        else:
            bot.reply_to(message, 'Неправильное название файла.')
    except Exception as e:
        bot.reply_to(message, 'Не был добавлен файл, меня не обманешь!')


@bot.message_handler(commands=['info'])
def send_info(message):
    bot.send_message(message.from_user.id,
                     'Этот бот нужен для поиска и скачивания и загрузки лабораторных работ')


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(non_stop=True, interval=0)
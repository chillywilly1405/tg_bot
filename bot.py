#импортируем всё необходимое
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import mysql.connector
#Создаём подключение к базе данных
mydb = mysql.connector.connect(host="localhost",user="root", password="root", database='backupschedule')
mycursor = mydb.cursor()

# Берём все кафедры из базы данных и создаём из них массив
mycursor.execute("SELECT DISTINCT kafter FROM infoSchedule")
result = mycursor.fetchall()

kafters = []

for i in result:
    kafters.append(i[0])
    

#Берём по кафедрам все группы и создаём словарь с ключом Кафедра и значением массив групп
groups = {}
buf = []
for i in kafters:
    mycursor.execute(f"SELECT DISTINCT group_kafter FROM infoSchedule where kafter = '{i}'")
    result = mycursor.fetchall()
    for j in result:
        buf.append(j[0])
    groups[i] = buf
    buf = []
    



# Состояния разговора внутри бота
SELECT_INFO,SELECT_USEFUL_CABINETS,SELECT_FEEDBACK,SELECT_INFO_ABOUT_KAFTERS,SELECT_FAQ, KAFTERS, GROUPS, COURSES = range(8)

# Настройка журналирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# ответ бота на сообщение /start
def start(update: Update, context):
    """Отправляет приветственное сообщение и предлагает выбрать кафедру."""

    reply_keyboard = [['Расписание', 'Кафедры'],
                      ['ВУЦ', 'Полезные кабинеты'],
                      ['FAQ', 'Обратная связь']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

    context.bot.send_message(chat_id=update.effective_chat.id, text='Привет! Я-бот-помощник,предоставляю расписание и прочую информацию студентам БГИТУ. '
                                                                    '\nВыберите интересующий вопрос:', reply_markup=reply_markup)
    return SELECT_INFO



# Функция выбора кафедры
def select_kafter(update: Update, context):
    """Сохраняет выбранную кафедру и предлагает выбрать группу."""
    # Записываем в context.user_data ту кафедру что выбрал человек
    context.user_data['kafter'] = update.message.text
    reply_keyboard = [[group] for group in groups[context.user_data['kafter']]]
    # После генерации кнопок групп добавляем в конец '/cancel' для того чтобы можно было начать выбор сначала
    reply_keyboard[0].append('/cancel')
    update.message.reply_text(
        'Теперь выберите группу:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    # Возвращаем состояние разговора
    return GROUPS


# Функция выбора группы
def select_group(update: Update, context):
    """Сохраняет выбранную группу и предлагает выбрать курс."""
    # Записываем в context.user_data ту группу что выбрал человек
    context.user_data['groups'] = update.message.text
    # Создаём массив кнопок и передаём его в сообщение
    reply_keyboard = [['1', '2'],
                      ['3', '4'],
                      ['5', '6', '/cancel']]
    update.message.reply_text(
        'Выберите курс:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,resize_keyboard=True)
    )
    # Возвращаем состояние разговора
    return COURSES


def select_info(update: Update, context):
    if update.message.text == "Расписание":
        # #Создаём массив кнопок и передаём его в сообщение
        reply_keyboard = [[kafter] for kafter in kafters]
        reply_keyboard.append(['/cancel'])
        update.message.reply_text(
            'Выберите кафедру:',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return KAFTERS
    if update.message.text == "ВУЦ":
        keyboard = [
            [
                InlineKeyboardButton("VK", url="https://vk.com/bgitu_vuts"),
                InlineKeyboardButton("Офф.сайт",
                                     url="http://www.bgitu.ru/universitet/voennyy-uchebnyy-tsentr/index.php"),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            'Вся доступная информация о ВУЦ в паблике VK и на сайте ВУЗа:',
            reply_markup=reply_markup
        )
    if update.message.text == "Кафедры":
        reply_keyboard = [['ИЛКЛАТиЭ', 'СИ'],
                          ['ИЭИ', '/cancel']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите кафедру:',
                                 reply_markup=reply_markup)
        return SELECT_INFO_ABOUT_KAFTERS
    if update.message.text == "Полезные кабинеты":
        reply_keyboard = [['Деканат', 'Библиотека'],
                          ['Бухгалтерия', '/cancel']]
        update.message.reply_text(
            'Выберите кабинет.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return SELECT_USEFUL_CABINETS
    if update.message.text == "FAQ":
        reply_keyboard = [['Кто такие кураторы?', 'Обязанности старосты'],
                          ['О стипендиях', '/cancel']]
        update.message.reply_text(
            'Выберите вопрос.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return SELECT_FAQ
    if update.message.text == "Обратная связь":
        update.message.reply_text("Если есть какие-то пожелания или хотите задать вопрос, то пишите на эту почту: bgitu@mail.ru")
        reply_keyboard = [['/cancel']]
        update.message.reply_text(
            'Нажмите /cancel, чтобы вернуться в главное меню.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return SELECT_FEEDBACK


def select_info_about_kafters(update: Update, context):
    if update.message.text == "ИЛКЛАТиЭ":
        update.message.reply_photo(photo="http://bgitu.ru/upload/medialibrary/efc/efcc677b1b827a44999701fa643b1134.jpg")
        update.message.reply_text(
            "Институт лесного комплекса, ландшафтной архитектуры, транспорта и экологии - (4832) 74-16-52 "
            "\nМестоположение: проспект Ленина,26 (учебный корпус №2)\nДиректор института – к.с/х.н., доцент Нартов Дмитрий Иванович"
        )
        reply_keyboard = [['ИЛКЛАТиЭ', 'СИ'],
                          ['ИЭИ', '/cancel']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите кафедру:',
                                 reply_markup=reply_markup)
        return SELECT_INFO_ABOUT_KAFTERS
    if update.message.text == "СИ":
        update.message.reply_photo(photo="http://bgitu.ru/upload/medialibrary/0fc/0fcf49f3d837b15fa3bf14b1ebbbf3e7.jpg")
        update.message.reply_text(
            "Строительный институт - (4832) 64-63-54"
            "\nМестоположение: проспект Станке Димитрова, 3 (учебный корпус №1)"
            "\nДиректор института - к.т.н., доцент Курбатская Наталья Александровна"
        )
        reply_keyboard = [['ИЛКЛАТиЭ', 'СИ'],
                          ['ИЭИ', '/cancel']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите кафедру:',
                                 reply_markup=reply_markup)
        return SELECT_INFO_ABOUT_KAFTERS
    if update.message.text == "ИЭИ":
        update.message.reply_photo(photo="http://bgitu.ru/upload/medialibrary/1e7/1e7757a6b408a097159d074b479ab918.jpg")
        update.message.reply_text(
            "Инженерно-экономический институт - (4832) 74-05-33"
            "\nМестоположение: проспект Ленина, 26А (учебный корпус №2А)"
            "\nДиректор института – д.э.н., профессор Кулагина Наталья Александровна"
        )
        reply_keyboard = [['ИЛКЛАТиЭ', 'СИ'],
                          ['ИЭИ', '/cancel']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите кафедру:',
                                 reply_markup=reply_markup)
        return SELECT_INFO_ABOUT_KAFTERS

def select_faq(update: Update, context):
    if update.message.text == "Кто такие кураторы?":
        update.message.reply_text(
            "Куратор — это один из преподавателей, который выполняет роль связующего звена между руководством кафедры, факультета или вуза и студентами группы. Он тесно сотрудничает со старостой группы, передает необходимую информацию. "
            "Зато, в отличие от школы, он практически не общается с родителями студентов. "
            "Одна из основных задач куратора группы студентов — помочь первокурсникам адаптироваться в вузе и влиться в учебный процесс. "
            "К нему можно обратиться с любым вопросом, который касается учебной деятельности."
        )
        reply_keyboard = [['Кто такие кураторы?', 'Обязанности старосты'],
                          ['О стипендиях', '/cancel']]
        update.message.reply_text(
            'Выберите вопрос.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return SELECT_FAQ
    if update.message.text == "Обязанности старосты":
        update.message.reply_text(
            "Права и обязанности старосты:"
            "\n1. Ведение журнала академической группы."
            "\n2. Посещение «старостатов» — специальных собраний для старост разных групп, которые проводит заместитель декана по воспитательной работе."
            "\n3. Непосредственное общение с представителями университетской администрации."
            "\n4. Организация взаимодействия группы и кафедры, деканата."
            "\n5. Выполнение текущих поручений руководства: собрать группу на мероприятие, распространить срочную информацию и так далее."
            "\n6. Отстаивать интересы и права группы."
            "\n7. В срок доводить всю важную информацию до одногруппников. "
        )
        reply_keyboard = [['Кто такие кураторы?', 'Обязанности старосты'],
                          ['О стипендиях', '/cancel']]
        update.message.reply_text(
            'Выберите вопрос.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return SELECT_FAQ
    if update.message.text == "О стипендиях":
        update.message.reply_photo(photo="https://sun9-77.userapi.com/impg/XvkSZsypPkI6cJVoI9u_YDCPp6zQAyXGfQPMxw/6Wsn2mGg24Q.jpg?size=1280x905&quality=95&sign=96aad39c1151618d88cf043b2c787aca&c_uniq_tag=CswM7R5rs1Kl4Wq2sL8c1tL8MlPfurHr1zBcEPCvHOM&type=album.jpg")
        update.message.reply_text("Размеры стипендий в БГИТУ🎁"

"\n✅2300 ₽ - минимальный размер Государственной Академической Стипендии (ГАС) высшего образования(ВО);"
"\n✅3450 ₽ - размер Государственной Социальной Стипендии (ГСС) высшего образования;"
"\n✅9550₽ - размер государственной стипендии Аспирантов, обучающихся по программам подготовки научно-педагогических кадров в аспирантуре по техническим и естественным направлениям подготовки, определенным Минобрнауки России;"
"\n✅3800 - размер государственной стипендии Аспирантов,обучающихся по программам подготовки научных и научно-педагогических кадров (за искл. гос. стипендии аспирантам, обучающимся по образовательным программам подготовки научно-педагогических кадров по направлениям подготовки, определенным Минобрнауки России)."

"\n✅700 ₽ - минимальный размер Государственной Академической Стипендии (ГАС) специального профессионального образования (СПО);"
"\n✅1050 ₽ - размер Государственной Социальной Стипендии (ГСС) СПО;"
        )
        reply_keyboard = [['Кто такие кураторы?', 'Обязанности старосты'],
                          ['О стипендиях', '/cancel']]
        update.message.reply_text(
            'Выберите вопрос.', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,resize_keyboard=True)
        )
        return SELECT_FAQ

def select_useful_cabinets(update: Update, context):
    if update.message.text == "Библиотека":
        update.message.reply_text(
            "Библиотека создана в 1930 году, в год основания Брянского лесотехнического института. "
            " Ее основной задачей является документальное и информационное обеспечение учебного процесса и научных исследований, воспитательная работа со студентами."
            " Книжный фонд библиотеки насчитывает свыше 400 тысяч изданий по всем направлениям учебной и научной деятельности академии."
            " Ежегодно услугами библиотеки пользуются более 14 000 читателей, которым выдается свыше 400 000 изданий."
            " Основные библиотечные процессы полностью автоматизированы, созданы два электронных читальных зала с бесплатным выходом в Интернет, функционирует локальная сеть, в читальных залах научной и учебной литературы работает беспроводной Интернет Wi-Fi."
            "\nДиректор библиотеки (каб. 315 корп. 2): Дракунова Ирина Александровна"
            "\nАдрес: 241037 г. Брянск, пр. Ст. Димитрова, 3 (1 корпус); Тел. (4832)64-99-14"
            "\n241050 г. Брянск, пр. Ленина, 26 (2 корпус); Tел. (4832)74-05-74"
            "\nEmail: biblio@bgitu.ru, drakunova@bgitu.ru"
        )
        reply_keyboard = [['Деканат', 'Библиотека'],
                          ['Бухгалтерия', '/cancel']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите кабинет:',
                                 reply_markup=reply_markup)
        return SELECT_USEFUL_CABINETS
    if update.message.text == "Деканат":
        update.message.reply_text(
            "Местоположение: проспект Ленина, 26А (учебный корпус №2А), 3 эт., 368 каб."
            "\nНомер телефона: 74-05-33"
        )
        reply_keyboard = [['Деканат', 'Библиотека'],
                          ['Бухгалтерия', '/cancel']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите кабинет:',
                                 reply_markup=reply_markup)
        return SELECT_USEFUL_CABINETS
    if update.message.text == "Бухгалтерия":
        update.message.reply_text(
            "Начальник управления: Садовникова Татьяна Викторовна"
            "Местоположение: проспект Станке Димитрова, 3 (учебный корпус №1), ауд. 235,237"
            "Телефон: 64-65-97"
        )
        reply_keyboard = [['Деканат', 'Библиотека'],
                          ['Бухгалтерия', '/cancel']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите кабинет:',
                                 reply_markup=reply_markup)
        return SELECT_USEFUL_CABINETS

def select_feedback(update: Update, context):
    if update.message.text == "Обратная связь":
        update.message.reply_text("Если есть какие-то пожелания или хотите задать вопрос, то пишите на эту почту: bgitu@mail.ru")
        reply_keyboard = [['Расписание', 'Кафедры'],
                          ['ВУЦ', 'Полезные кабинеты'],
                          ['FAQ', 'Обратная связь']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

        context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите интересующую вас информацию:',
                                 reply_markup=reply_markup)
        return SELECT_FEEDBACK





    # функция выбора курса и вывода расписания
def select_course(update: Update, context):
    """Выводит расписание выбранной группы и завершает разговор."""
    # Записываем в context.user_data тот курс что выбрал человек
    context.user_data['course'] = update.message.text
    # Делаем запрос на получение расписания к базе данных
    mycursor.execute(
        f"SELECT schedule FROM infoschedule WHERE kafter = '{context.user_data['kafter']}' and group_kafter = '{context.user_data['groups']}' and course = {context.user_data['course']}")
    расписание_группы = mycursor.fetchone()
    # Если было что то возращено то значит такое было найдено и выводим расписание
    if расписание_группы != None:
        update.message.reply_text(
            f"Расписание для {context.user_data['groups']}, {context.user_data['course']} курс:\n{расписание_группы[0]}",
            reply_markup=ReplyKeyboardMarkup([['/start']], one_time_keyboard=True))
    else:
        # Иначе выводим что расписание для такой группы и такого курса ещё не было добавлено
        update.message.reply_text(
            f"Расписание для {context.user_data['groups']}, {context.user_data['course']} курс: ещё не было добавлено",
            reply_markup=ReplyKeyboardMarkup([['/start']], one_time_keyboard=True))
    reply_keyboard = [[kafter] for kafter in kafters]
    reply_keyboard.append(['/cancel'])
    update.message.reply_text(
        'Если хочешь узнать ещё расписание выбери новую кафедру:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return KAFTERS


# Ответ бота на сообщение /cancel
def cancel(update: Update, context):
    """Отменяет разговор и завершает его без выбора расписания."""
    reply_keyboard = [['Расписание', 'Кафедры'],
                      ['ВУЦ', 'Полезные кабинеты'],
                      ['FAQ', 'Обратная связь']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

    context.bot.send_message(chat_id=update.effective_chat.id, text='Выбери интересующую вас информацию:',
                             reply_markup=reply_markup)
    # Переходит в начальное состояние
    return SELECT_INFO


# главная функция
def main():
    # Соединение с ботом по токену
    updater = Updater("6273671398:AAFrytlkX6E6utMrqjZTWb59a4FsrdtLosM")

    # Получение диспетчера для регистрации обработчиков
    dp = updater.dispatcher

    # Создание обработчиков команд
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SELECT_INFO: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')), select_info)],
            SELECT_INFO_ABOUT_KAFTERS: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')),
                                                       select_info_about_kafters)],
            SELECT_FEEDBACK: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')), select_feedback)],
            SELECT_FAQ: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')), select_faq)],
            KAFTERS: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')), select_kafter)],
            GROUPS: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')), select_group)],
            COURSES: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')), select_course)],
            SELECT_USEFUL_CABINETS: [MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Отмена$')), select_useful_cabinets)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Регистрация обработчика разговоров в диспетчере
    dp.add_handler(conv_handler)

    # Запуск бота
    updater.start_polling()

    # Остановка бота при получении сигнала прерывания (Ctrl+C)
    updater.idle()


# Запускаем главную функцию
if __name__ == '__main__':
    main()

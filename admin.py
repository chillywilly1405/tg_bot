#импортируем всё необходимое
from flask import Flask, render_template, request
import os
import mysql.connector
#Создаём подключение к базе данных
mydb = mysql.connector.connect(host="localhost",user="root", password="root", database='backupschedule')

#Создаём фласк приложение
app = Flask(__name__)

#Декоратор который даёт понять что мы создаём роут / который поддерживает get и post запросы
@app.route('/', methods=['GET', 'POST'])
def upload_schedule():
    #Если на роут '/' был отправлен пост запрос
    if request.method == 'POST':
        #берём все полученные через пост запрос данные с формы
        kafter = request.form['kafter']
        group = request.form['group']
        course = request.form['course']
        #и файл
        file = request.files['file']
        # Сохранение файла расписания для группы
        file.save(f'{group}.txt')
        #Читаем информацию с него
        with open(f'{group}.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        #и удаляем его чтобы не засорял папку проекта
        os.remove(f'{group}.txt')
        #создаём курсор для базы данных
        mycursor = mydb.cursor()
        #Делаем выборку из базы данных есть ли расписание для такой кафедры группы и курса
        mycursor.execute(f"SELECT schedule FROM infoschedule WHERE kafter = '{kafter}' and group_kafter = '{group}' and course = {course}")
        #берём один результат (он всегда будет один или его не будет потому что мы либо записываем новое расписание либо изменяем старое)
        result = mycursor.fetchone()
        #Проверяем было ли возращено что то в запросе
        if result == None:
            #Если нет то добавляем новое расписание для кафедры группы курса которую указале в форме
            mycursor.execute(f"INSERT INTO infoSchedule values ('{kafter}', '{group}', {course}, '{content}')")
            mydb.commit()
            #И возращаем на форму сообщение о том что было успешно добавлено расписание
            return render_template('upload.html', data=f"Расписание для группы {group} курса {course} было успешно добавлено!")
            
        else:
            #Если расписание есть то мы меняем уже имеющееся на то которое было загружено в форме
            mycursor.execute(f"UPDATE infoSchedule SET schedule = '{content}' WHERE kafter = '{kafter}' and group_kafter = '{group}' and course = {course}")
            mydb.commit()
            #И возращаем на форму сообщение о том что было успешно обновлено расписание
            return render_template('upload.html', data=f"Расписание для группы {group} курса {course} было успешно обновлено!")
    #Если Get то просто рендерим шаблон
    return render_template('upload.html')

if __name__ == '__main__':
    app.run()

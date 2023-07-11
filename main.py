import pytesseract
from fastapi import FastAPI, UploadFile, File
import os
from pdf2image import convert_from_path
from datetime import datetime

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\mnt\tesseract_FastAPI\Tesseract-OCR\tesseract.exe"



@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.join(current_dir, "uploads", file.filename)
    with open(file_path, "wb") as f:
        contents = await file.read()
        f.write(contents)


    if file_path[-4:] == '.pdf':
        path = '../tesseract_FastAPI/page0.jpg'
        images = convert_from_path(file_path, 150, poppler_path=r'C:\Users\mnt\tesseract_FastAPI\poppler-23.05.0\Library\bin')

        if os.path.isfile(path):
            os.remove(path)

        for i in range(len(images)):
            images[i].save('page' + str(i) + '.jpg', 'JPEG')

        file_path = path
        result = pytesseract.image_to_string(file_path, lang='rus')

    elif file_path[-4:] == '.png' or file_path[-4:] == '.jpg':
        result = pytesseract.image_to_string(file_path, lang='rus')

    operation = {"sender": "",
                 "receiver": "",
                 "amount": 0,
                 "currency": "",
                 "datetime": "",
                 "type": 0,
                 # тип перевода: sbp, p2p, qr;
                 "transfer_type:": ""}


    result = result.split('\n')

    result = list(filter(None, result))

    if result[0][-9:] == 'СБЕР БАНК' or result[0][-8:] == 'СБЕРБАНК':
        operation['type'] = 0
        for line_num in range(len(result)):
            if line_num == 2:
                date_list = result[line_num].split()
                print(date_list)

                months_dict = {
                    'января': '01',
                    'февраля': '02',
                    'марта': '03',
                    'апреля': '04',
                    'мая': '05',
                    'июня': '06',
                    'июля': '07',
                    'авгуса': '08',
                    'сентября': '09',
                    'октября': '10',
                    'ноября': '11',
                    'декабря': '12'
                }
                if date_list[-1] == '(МСК)':
                    timezone = '+0300'

                time = date_list[3].split(':')

                print(time)

                date = date_list[0] + '.' + months_dict[date_list[1]] + '.' + date_list[2] + ' ' + time[0] + '.' + time[
                    1] + '.' + time[2] + timezone

                date_format = '%d.%m.%Y %H.%M.%S%z'
                date = datetime.strptime(date, date_format)


                operation['datetime'] = date
            if line_num == 6:
                operation['receiver'] = result[line_num]

            if line_num == 12:
                operation['sender'] = result[line_num]

            if line_num == 16:
                amount = result[line_num][:-1].split(',')

                if len(amount[0]) > 3:
                    amount_many = amount[0].split()
                    amount[0] = amount_many[0] + amount_many[1]

                amount = amount[0] + '.' + amount[1]

                if amount[-1] == ' ':
                    amount = amount[:-1]

                print(amount)

                operation['amount'] = float(amount)

                if result[line_num][-1] == 'Р':
                    operation['currency'] = "rub"



    elif result[0][-8:] == 'тинькоФФ':
        operation['type'] = 1
        for line_num in range(len(result)):
            if line_num == 1:
                """буква "T" в выводе означает разделитель между датой и временем в формате ISO 8601, 
                который является стандартным форматом представления даты и времени."""
                date_format = '%d.%m.%Y %H.%M.%S'
                date = result[line_num].split()
                time = date[1].split(':')
                time = time[0] + '.' + time[1] + '.' + time[2]
                print(time)
                date_time = date[0] + ' ' + time
                date = datetime.strptime(date_time, date_format)
                formatted_date = date.strftime('%d.%m.%Y %H:%M:%S')
                #operation['datetime'] = formatted_date
                operation['datetime'] = date

            if line_num == 2:

                print(result[line_num])

                operation['amount'] = float(result[line_num][6:-2])
                if result[line_num][-1] == "Р":
                        operation['currency'] = "rub"
                # возвращать значение самого поля
            if line_num == 6:
                operation['sender'] = result[line_num][len('Отправитель') + 1:]
            if line_num == 8:
                operation['receiver'] = result[line_num][len('Получатель') + 1:]

    # Возвращаем информацию о сохраненном файле
    return operation


import datetime
import re
import time

import requests
import xlrd
import xlsxwriter
from bs4 import BeautifulSoup
from gettext import find



def wait(ms):
    # интервал 50 мс - это гарантированных два-три нажатия на клавишу:
    n = ms // 50
    for i in range(n):
        time.sleep(0.05)



def replace_spaсe(string):
    string = string.replace(" ", "")
    string = string.replace(".", "_")
    return string



def get_link(source_data):  # вытаскиваем из строки ссылку на картинку jpg из fancybox
    # примеры ссылок: <a href = "http://modelart111.com/images/1-43 amr bbr spark aston db4 zagato (5).jpeg?osCsid=b717654755ecf
    # 17c4f89be9a645ae528" rel = "fancybox" target="_blank"><img alt="" height="1254" src="images/1-43 amr bbr spark aston db4 zagato (5).jpeg"
    # width="1672"/></a>

    # т.е. в исходной строке ссылка начинается на "http" и заканчивается расширением .images
    # source_data передаётся в функцию как string (преобразование не нужно)

    url_start_index = source_data.find("http")
    url_stop_index = source_data.find(".jpeg")

    url_link_jpg = source_data[url_start_index:(url_stop_index + 5)]

    if url_stop_index == -1:
        url_stop_index = source_data.find(".jpg")
        url_link_jpg = source_data[url_start_index:(url_stop_index + 4)]

    if url_stop_index == -1:
        url_stop_index = source_data.find(".JPG")
        url_link_jpg = source_data[url_start_index:(url_stop_index + 4)]

    if url_start_index == -1 or url_stop_index == -1:
        return ""
    else:
        return url_link_jpg



def get_picture(url_picture):
    #url_picture ="http://modelart111.com/product_info.php?cPath=2_23&products_id=2899&osCsid=1a78cdf1b214695832c2b80b537dcd32"
    page_picture = requests.get(url_picture)

    soup_picture = BeautifulSoup(page_picture.content, "html.parser")  # html.parser встроен в Python

    # вевести на печать всю страницу (для тестирования):
    # print(soup_picture.prettify())

    data_picture = soup_picture.find_all("a", rel="fancybox")

    # print("Это data_picture: " + str(data_picture))

    for data_picture in data_picture:

        # преобразовываем ссылку на изображение:
        source_data = str(data_picture)
        url_link_jpg = get_link(source_data)

        print(url_link_jpg)

        if url_link_jpg == " ":
            continue

        # сохраняем рисунок:
        img_data = requests.get(url_link_jpg).content
        with open(data_picture.find_next("img").get("src"), "wb") as handler:
            handler.write(img_data)



def main(search_word):  # search_word = "F. Suber"
    # "Текущая дата и время:
    now = datetime.datetime.now()
    excel_file_name = "Report/" + replace_spaсe(search_word) + "_" + now.strftime("%Y_%m_%d_%H_%M_%S") + ".xlsx"

    # создаём новый файл Excel и открываем его на запись:
    workbook = xlsxwriter.Workbook(excel_file_name)

    # добавляем новый лист в файл xlsx
    worksheet = workbook.add_worksheet(search_word)

    #добавляем новый формат для выравнивание столбца D по правому краю:
    cell_format = workbook.add_format({'align': 'right'})

    result_pages_num = 0   # номер поисковой страницы на сайте Modelart111.com
    excel_row_num    = 0   # Номер строки таблицы результатов Excel

    while True:
        result_pages_num += 1
        url = "https://modelart111.com/index.php?cPath=2_23&sort=2a&page=" + str(result_pages_num)
        page = requests.get(url)

        soup = BeautifulSoup(page.content, "html.parser")  # html.parser встроен в Python

        # вевести на печать всю страницу (для тестирования):
        # print(soup.prettify())

        print("========================")
        print("Page " + str(result_pages_num))

        # поиск по ключевому слову:
        data1 = soup.find_all("a", string=re.compile(search_word))

        for data1 in data1:
            excel_row_num += 1

            # "случайный рекламный лот внизу" вызовет ошибку преобразования None в text:
            if data1.find_next("td") is None:
                excel_row_num -= 1
                continue
            else:
                worksheet.write(excel_row_num-1, 0, excel_row_num)
                worksheet.write(excel_row_num-1, 1, data1.get("href"))  # ссылка на страницу модели
                worksheet.write(excel_row_num-1, 2, data1.text)  # текстовка
                worksheet.write(excel_row_num-1, 3, data1.find_next("td").text, cell_format)  # следующий тег

                # сохраняем картинки jpeg/jpg из галереи "fancybox"
                get_picture(data1.get("href"))

            # вывод результатов на печать:
            print(data1.get("href") + " " + data1.text + " " + data1.find_next("td").text)

        print("========================")

        if soup.find("a", title=re.compile("Next Page")) == None:
            print("Не нашли Next, поэтому цикл останавливаем")

            # настраиваем ширину столюцов:
            worksheet.set_column("A:A", 4)
            worksheet.set_column("B:B", 110)
            worksheet.set_column("C:C", 60)
            worksheet.set_column("D:D", 10)

            # сохраняем и закрываем файл Excel
            workbook.close()
            return

        # ждём секунду, чтобы не забанили:
        wait(500)



if __name__ == '__main__':
    main("F. Suber")
    # main("Barnett S.")

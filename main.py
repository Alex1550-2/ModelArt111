""" Основной модуль программы парсинга сайта modelart111.com
"""
import argparse
import datetime
import re
from typing import Union

import requests
import xlsxwriter
from bs4 import BeautifulSoup

from utils import wait


# определяем аргументы скрипта при использовании анализатора argparse:
# вызов описания аргументов: python main -h
parser = argparse.ArgumentParser(
    description="modelart111.com: Search all models by builder name"
)
parser.add_argument(
    "buildername", type=str, help="The name of the builder scale cars: 'Suber' or 'Barnett'"
)
parser.add_argument(
    "savefoto", type=str, help="Save foto models options: 'yes'"
)
args = parser.parse_args()


# словарь с именами сборщиков и их интерпритацией с сайта modelart111.com
switch = {
    "Suber": "F. Suber",
    "Barnett": "Barnett S.",
}


def replace_symbol(string: str) -> str:
    """Функция возвращает строку без запрещённых / нежелательных символов в имени файла"""
    string = string.replace(" ", "")
    string = string.replace(".", "_")
    return string


def write_file_excel(search_word: str, dictionary_list: list[dict[str, Union[str, int]]]):
    """Функция сохраняет данные из списка словарей dictionary_list[] в файл Excel"""
    now = datetime.datetime.now()  # команда now - текущее дата/время
    excel_file_name = (
        "Report/"
        + replace_symbol(search_word)
        + "_"
        + now.strftime("%Y_%m_%d_%H_%M_%S")
        + ".xlsx"
    )

    # создаём новый файл Excel и открываем его на запись:
    workbook = xlsxwriter.Workbook(excel_file_name)

    # добавляем новый лист в файл xlsx
    worksheet = workbook.add_worksheet(search_word)

    # добавляем новый формат для выравнивание столбца D по правому краю:
    cell_format = workbook.add_format({"align": "right"})

    # настраиваем ширину столюцов файла xlsx:
    worksheet.set_column("A:A", 4)
    worksheet.set_column("B:B", 110)
    worksheet.set_column("C:C", 60)
    worksheet.set_column("D:D", 10)

    dictionary_length = len(dictionary_list)
    for excel_row_num in range(0, dictionary_length):
        worksheet.write(excel_row_num, 0, dictionary_list[excel_row_num]["num"])
        worksheet.write(excel_row_num, 1, dictionary_list[excel_row_num]["link"])
        worksheet.write(excel_row_num, 2, dictionary_list[excel_row_num]["text"])
        worksheet.write(
            excel_row_num, 3, dictionary_list[excel_row_num]["price"], cell_format
        )

    # сохраняем и закрываем файл Excel:
    workbook.close()


def get_link(source_data: str) -> str:
    """вытаскиваем из строки ссылку на картинку jpg из fancybox
    примеры ссылок: <a href = "http://modelart111.com/images/1-43 amr bbr spark aston db4 za
    gato (5).jpeg?osCsid=b717654755ecf17c4f89be9a645ae528" rel = "fancybox" target="_blank">
    <img alt="" height="1254" src="images/1-43 amr bbr spark aston db4 zagato (5).jpeg"
    width="1672"/></a>

    т.е. в исходной строке ссылка начинается на "http" и заканчивается расширением .images
    source_data передаётся в функцию как string (преобразование не нужно)
    """
    url_start_index = source_data.find("http")

    search_stop_phrase = ".jpeg"
    url_stop_index = source_data.find(search_stop_phrase)

    if url_stop_index == -1:
        search_stop_phrase = ".jpg"
        url_stop_index = source_data.find(search_stop_phrase)

    if url_stop_index == -1:
        search_stop_phrase = ".JPG"
        url_stop_index = source_data.find(search_stop_phrase)

    if url_start_index == -1 or url_stop_index == -1:
        url_link_jpg = ""

    else:
        url_link_jpg = source_data[
            url_start_index : (url_stop_index + len(search_stop_phrase))
        ]

    return url_link_jpg


def get_picture(url_picture: str):
    """Функция открывает страницу сайта modelart111.com по ссылке url_picture
    и сохраняет в папке "images" все найденные в галерее "fancybox" изображения jpeg/jpg

    пример ссылки url_picture ="http://modelart111.com/product_info.php?cPath=
    2_23&products_id=2899&osCsid=1a78cdf1b214695832c2b80b537dcd32"
    """
    page_picture = requests.get(url_picture)

    soup_picture = BeautifulSoup(
        page_picture.content, "html.parser"
    )  # html.parser встроен в Python

    # вевести на печать всю страницу (для тестирования):
    # print(soup_picture.prettify())

    links_picture_list = soup_picture.find_all("a", rel="fancybox")

    for picture_href in links_picture_list:

        # преобразовываем ссылку на изображение:
        source_data = str(picture_href)
        url_link_jpg = get_link(source_data)

        print(url_link_jpg)

        if url_link_jpg == " ":
            continue

        # сохраняем рисунок:
        img_data = requests.get(url_link_jpg).content
        with open(picture_href.find_next("img").get("src"), "wb") as handler:
            handler.write(img_data)


def main():
    """Функция позволяет осуществлять поиск содержимого сайта modelart111.com
    по ключевому слову search_word - имя сборщика, например "F. Suber" / "Barnett S."

    Ключевое слово по написанию должно совпадать с сайтом modelart111.com
    """

    # определяем аргументы скрипта:
    search_word: str = switch.get(str(args.buildername))   # имя сборщика
    ask: str = args.savefoto   # сохраняем фото или нет

    if search_word == None:
        print("Имя сборщика не найдено!")
        return

    print(f"Поисковое слово: {search_word}")

    result_pages_num = 0  # номер поисковой страницы на сайте Modelart111.com

    dictionary_list = []  # основной список словарей с результатами поиска
    list_row_num = 0  # Номер строки списка словарей

    while True:
        result_pages_num += 1
        url = (
            "https://modelart111.com/index.php?cPath=2_23&sort=2a&page="
            + str(result_pages_num)
        )
        page = requests.get(url)

        soup = BeautifulSoup(
            page.content, "html.parser"
        )  # html.parser встроен в Python

        # вевести на печать всю страницу (для тестирования):
        # print(soup.prettify())

        print("========================")
        print(f"Page {str(result_pages_num)}")

        # поиск "ссылок на предметы" по ключевому слову:
        items_link_list = soup.find_all("a", string=re.compile(search_word))

        for item_href in items_link_list:
            list_row_num += 1

            # "случайный рекламный лот внизу" вызовет ошибку преобразования None в text:
            if item_href.find_next("td") is None:
                list_row_num -= 1
                continue

            dictionary_list.append(
                {
                    "num": list_row_num,
                    "link": item_href.get("href"),
                    "text": item_href.text,
                    "price": item_href.find_next("td").text,
                }
            )

            # сохраняем картинки jpeg/jpg из галереи "fancybox"
            if ask == "yes":
                get_picture(item_href.get("href"))

            # вывод результатов на печать (текущий словарь из списка):
            print(dictionary_list[list_row_num - 1])

        print("========================")

        if (
            soup.find("a", title=re.compile("Next Page")) is None
            or result_pages_num > 50
        ):
            # Условием выхода из бесконечного цикла является последовательный перебор
            # всех "продуктовых" страниц сайта до последней, на которой нет title "Next Page"
            # ИЛИ
            # аварийный выход - просмотр больше 50 поисковых страниц
            print("Не нашли Next, поэтому цикл останавливаем")

            # сохраняем данные из списка словарей dictionary_list[] в файл Excel:
            write_file_excel(search_word, dictionary_list)
            return

        # ждём, чтобы не забанили:
        wait(500)


if __name__ == "__main__":
    main()

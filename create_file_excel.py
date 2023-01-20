import datetime

import xlsxwriter


def replace_symbol(string: str) -> str:
    """Функция возвращает строку без запрещённых / нежелательных символов в имени файла"""
    string = string.replace(" ", "")
    string = string.replace(".", "_")
    return string


def create_file_excel(search_word):
    # "Текущая дата и время:
    now = datetime.datetime.now()
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

    worksheet.write(0, 0, "0")

    # сохраняем и закрываем файл Excel
    workbook.close()

    return excel_file_name


create_file_excel("F. Suber")

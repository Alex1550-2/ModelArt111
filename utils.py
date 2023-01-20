""" Вспомогательный модуль. Содержит универсальные функции
"""
import time


def wait(time_interval: int):
    """Функция разделяет процесс ожидания на отдельные интервалы ms,
    позволяя реализовать прерывание процесса sleep непосредственно во время процесса sleep
    """
    delta_sleep: int = (
        50  # интервал 50 мс - это гарантированных два-три нажатия на клавишу
    )
    step_sleep = time_interval // delta_sleep

    i: int = 1
    while i < step_sleep:
        i += 1
        time.sleep(0.05)


def replace_symbol(string: str) -> str:
    """Функция возвращает строку без запрещённых / нежелательных символов в имени файла"""
    string = string.replace(" ", "")
    string = string.replace(".", "_")
    return string

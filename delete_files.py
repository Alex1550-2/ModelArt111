import os  # модуль для работы с операционной системой

# удалить все файлы из папок "Report" и "images":
def delete_files(dir_name):
    # dir_name = "Report/"
    files = os.listdir(dir_name)
    for files in files:
        files = dir_name + files
        print("Файл " + files + " удалён")
        os.remove(files)

delete_files("Report/")
delete_files("images/")

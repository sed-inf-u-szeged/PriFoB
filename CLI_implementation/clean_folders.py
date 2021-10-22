import os
import shutil


def clean():
    for folder in os.listdir('local_files'):
        folder_path = os.path.join('local_files', folder)
        if os.path.isdir(folder_path):
            try:
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
            except Exception as e:
                print(e)


clean()

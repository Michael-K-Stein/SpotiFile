import os
from zipfile import ZipFile
import time
import sys


class ZipUtilities:

    def toZip(self, files, filename):
        zip_file = ZipFile(filename, 'w')
        for file in files:
            if os.path.isfile(file):
                    zip_file.write(file)
            else:
                self.addFolderToZip(zip_file, file)
        zip_file.close()

    def addFolderToZip(self, zip_file, folder):
        print(f'Adding folder {folder} to archive {zip_file}')
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path):
                print('File added: ' + str(full_path))
                zip_file.write(full_path)
            elif os.path.isdir(full_path):
                print('Entering folder: ' + str(full_path))
                self.addFolderToZip(zip_file, full_path)


def get_directory_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def get_zip_name() -> str:
    return f'{sys.argv[2]}/Download_{str(time.time())}.zip'


def zip_dirs(dir_list:list) -> str:
    zname = get_zip_name()
    utilities = ZipUtilities()
    utilities.toZip(dir_list, zname)


def zip_bunches(start_path:str='music', max_zip_size:int=3813764863):
    current_bunch = []
    current_bunch_size = 0
    for dir_name in os.listdir(start_path):
        dir_path = os.path.join(start_path, dir_name)
        dir_size = get_directory_size(dir_path)
        print(f'Dir: {dir_path} of size {dir_size}')
        if current_bunch_size + dir_size < max_zip_size:
            current_bunch.append(dir_path)
            current_bunch_size += dir_size
        else:
            zip_dirs(current_bunch)
            current_bunch.clear()
            current_bunch_size = 0
    zip_dirs(current_bunch)
    current_bunch.clear()
    current_bunch_size = 0


if __name__ == '__main__':
    if len(sys.argv) == 1:
        zip_bunches()
    else:
        zip_bunches(sys.argv[1])
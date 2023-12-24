import os

BG_DIR_PATH = r'F:\GitFile\BA_OST_Index_Site_Static\static\images\background'
DATA_DIR_PATH = "ost_data"
ALL_FILES = filter(lambda x: os.path.isfile(os.path.join(BG_DIR_PATH, x)), os.listdir(BG_DIR_PATH))

files_to_remove = []
for i in ALL_FILES:
    if i.endswith('kr.jpg'):
        files_to_remove.append(i)

for i in files_to_remove:
    os.remove(os.path.join(BG_DIR_PATH, i))

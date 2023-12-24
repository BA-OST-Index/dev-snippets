import os
import json
import shutil
import datetime
import opencc
from .reader import StoryInfoTxtReader, I18N as I18N_POOL
from .file_tool import FileReader
from zh_cn_converter.text_converter import i18nFileLoader, ALL_CONVERTER

EXPORT_FOLDER = ""
DATA_POOL = []
CN_TO_TW = opencc.OpenCC("s2twp.json")

__all__ = ["convert_file", "delete_old_file", "export_data"]


def convert_file(filepath):
    global EXPORT_FOLDER

    FILEPATH = filepath
    EXPORT_FOLDER = os.path.join(os.path.split(filepath)[0], "exported")

    with FileReader(FILEPATH) as reader:
        while True:
            try:
                reader.readline()
            except EOFError:
                break

            if reader.last_read_autoflag == ";;":
                DATA_POOL.append(StoryInfoTxtReader(reader))

        reader.rewrite_file()


def delete_old_file():
    # remove the previous result first
    shutil.rmtree(EXPORT_FOLDER, ignore_errors=True)
    os.makedirs(EXPORT_FOLDER, exist_ok=True)


def export_data():
    # export data
    I18N_POOL.to_json(os.path.join(EXPORT_FOLDER, "i18n_original.json"))
    for i in DATA_POOL:
        # create folder for the dedicated file
        target_path = os.path.join(EXPORT_FOLDER, i.filepath)
        os.makedirs(os.path.split(target_path)[0], exist_ok=True)

        with open(target_path, "w", encoding="UTF-8") as file:
            json.dump(i.json_result, file, indent=2, ensure_ascii=False)
    with open(os.path.join(EXPORT_FOLDER, "creation_time.txt"), "w", encoding="UTF-8") as file:
        file.write(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S (Local Time)")))

    # auto convert data
    ALL_LANG_LIST = ["zh_cn_cn", "zh_cn_jp", "zh_cn_tw", "zh_tw"]
    original_i18n = i18nFileLoader(EXPORT_FOLDER, ALL_LANG_LIST,
                                   "i18n_output.json")
    original_i18n.set_original_filepath(os.path.join(EXPORT_FOLDER, "i18n_original.json"))
    original_i18n.add_converters(*ALL_CONVERTER)
    original_i18n.normalize_origin_file()

    result = original_i18n.convert()
    result[ALL_LANG_LIST.index("zh_tw")] = CN_TO_TW.convert(result[ALL_LANG_LIST.index("zh_tw")])

    for (lang, content) in zip(ALL_LANG_LIST, result):
        with open(os.path.join(EXPORT_FOLDER, "i18n_" + lang + ".json"), "w", encoding="UTF-8") as file:
            file.write(content)

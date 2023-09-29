import json
import os

UPDATE_DATA = False

if UPDATE_DATA:
    __import__("data_updater")


class ZhConverter:
    def __init__(self, data_path, text_flag):
        with open(data_path, mode="r", encoding="UTF-8") as file:
            self.data = json.load(file)
        self.zh_cn_jp = [i[0] for i in self.data]
        self.zh_cn_cn = [i[1] for i in self.data]
        self.zh_cn_tw = [i[2] for i in self.data]
        self.zh_tw = [i[3] for i in self.data]
        self.text_flag = text_flag

    def auto_normalize(self, text: str):
        """将文本归化成 zh_cn_jp 版本后进行处理"""
        text2 = self.convert(self.convert(text, "zh_cn_cn", "zh_cn_jp", True), "zh_cn_tw", "zh_cn_jp", True)
        return text2

    def convert(self, text: str, original_lang: str, target_lang: str, keep_flag: bool):
        text2 = text
        ori_lang = self._select_lang_dataset(original_lang)
        tar_lang = self._select_lang_dataset(target_lang)
        for (ori, tar) in zip(ori_lang, tar_lang):
            if keep_flag:
                text2 = text2.replace("{" + self.text_flag + ori + "}",
                                      "{" + self.text_flag + tar + "}")
            else:
                text2 = text2.replace("{" + self.text_flag + ori + "}", tar)
        return text2

    def _select_lang_dataset(self, lang_name: str):
        if lang_name == "zh_cn_jp": return self.zh_cn_jp
        if lang_name == "zh_cn_cn": return self.zh_cn_cn
        if lang_name == "zh_cn_tw": return self.zh_cn_tw
        if lang_name == "zh_tw": return self.zh_tw
        raise ValueError


class i18nFileLoader:
    """这个类的逻辑是：先提供输出文件位置，再提供原始文件位置，最后转换。"""

    def __init__(self, folder_path: str, lang_list: list, filename: str):
        self.output_lang_list = lang_list
        self.all_output_filepaths = [os.path.join(folder_path, lang, filename) for lang in lang_list]
        self.origin_file = ""
        self.converter: list[ZhConverter, ...] = []

    def set_original_filepath(self, filepath: str):
        with open(filepath, mode="r", encoding="UTF-8") as file:
            self.origin_file = file.read()

    def normalize_origin_file(self):
        for i in self.converter:
            self.origin_file = i.auto_normalize(self.origin_file)

    def add_converters(self, *converters: ZhConverter):
        self.converter.extend(converters)

    def convert_and_output(self):
        if self.origin_file == "":
            raise ValueError("请先调用 set_original_filepath 设置源文件位置及语言参数")

        for (lang, filepath) in zip(self.output_lang_list, self.all_output_filepaths):
            text2 = self.origin_file
            for converter in self.converter:
                text2 = converter.convert(text2, "zh_cn_jp", lang, False)
            with open(filepath, mode="w", encoding="UTF-8") as file:
                file.write(text2)


converter_stu_first = ZhConverter("data/stu_first.json", "cf")
converter_stu_last = ZhConverter("data/stu_last.json", "cl")
converter_character_first = ZhConverter("data/char_first.json", "cf")
converter_school = ZhConverter("data/l10n_school_short.json", "sn")
converter_club = ZhConverter("data/l10n_club.json", "cn")
converter_etc = ZhConverter("data/etc.json", "et")
all_converter = [converter_stu_first, converter_stu_last, converter_character_first, converter_school, converter_club,
                 converter_etc]

data_story = i18nFileLoader(r"../ost_data/i18n", ["zh_cn_cn", "zh_cn_jp", "zh_cn_tw", "zh_tw"],
                            "story.json")
data_story.set_original_filepath(r"../ost_data/i18n/zh_cn_tw/_source/story.json")

data_story_bond = i18nFileLoader(r"../ost_data/i18n", ["zh_cn_cn", "zh_cn_jp", "zh_cn_tw", "zh_tw"],
                                 "story_bond.json")
data_story_bond.set_original_filepath(r"../ost_data/i18n/zh_cn_tw/_source/story_bond.json")

data_story_all = i18nFileLoader(r"../ost_data/i18n", ["zh_cn_cn", "zh_cn_jp", "zh_cn_tw", "zh_tw"],
                                "story_all.json")
data_story_all.set_original_filepath(r"../ost_data/i18n/zh_cn_tw/_source/story_all.json")

all_data = [data_story, data_story_bond, data_story_all]
for i in all_data:
    i.add_converters(*all_converter)
    i.normalize_origin_file()
    i.convert_and_output()

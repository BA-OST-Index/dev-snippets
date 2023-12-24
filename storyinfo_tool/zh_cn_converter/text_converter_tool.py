import json
import os


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
        if lang_name == "zh_cn_jp":
            return self.zh_cn_jp
        if lang_name == "zh_cn_cn":
            return self.zh_cn_cn
        if lang_name == "zh_cn_tw":
            return self.zh_cn_tw
        if lang_name == "zh_tw":
            return self.zh_tw
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

    def convert(self) -> list:
        if self.origin_file == "":
            raise ValueError("请先调用 set_original_filepath 设置源文件位置及语言参数")

        result = []
        for lang in self.output_lang_list:
            text2 = self.origin_file
            for converter in self.converter:
                text2 = converter.convert(text2, "zh_cn_jp", lang, False)
            result.append(text2)

        return result

    def convert_and_write(self):
        for (filepath, content) in zip(self.all_output_filepaths, self.convert()):
            with open(filepath, mode="w", encoding="UTF-8") as file:
                file.write(content)

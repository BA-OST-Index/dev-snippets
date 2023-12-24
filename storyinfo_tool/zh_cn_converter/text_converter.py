import os
from .text_converter_tool import ZhConverter, i18nFileLoader

UPDATE_DATA = False

if UPDATE_DATA:
    __import__("zh_cn_converter.data_updater")

CONVERSION_DATA_PATH = os.path.join(os.path.split(__file__)[0], "data")
_data_path_joiner = lambda path: os.path.normpath(os.path.join(CONVERSION_DATA_PATH, path))

CONVERTER_STU_FIRST = ZhConverter(_data_path_joiner("stu_first.json"), "cf")
CONVERTER_STU_LAST = ZhConverter(_data_path_joiner("stu_last.json"), "cl")
CONVERTER_CHAR_FIRST = ZhConverter(_data_path_joiner("char_first.json"), "cf")
CONVERTER_SCHOOL = ZhConverter(_data_path_joiner("l10n_school_short.json"), "sn")
CONVERTER_CLUB = ZhConverter(_data_path_joiner("l10n_club.json"), "cn")
CONVERTER_ETC = ZhConverter(_data_path_joiner("etc.json"), "et")
ALL_CONVERTER = [CONVERTER_STU_FIRST, CONVERTER_STU_LAST, CONVERTER_CHAR_FIRST, CONVERTER_SCHOOL, CONVERTER_CLUB,
                 CONVERTER_ETC]


def convert_ost_data():
    data_story = i18nFileLoader(r"../../ost_data/i18n", ["zh_cn_cn", "zh_cn_jp", "zh_cn_tw", "zh_tw"],
                                "story.json")
    data_story.set_original_filepath(r"../ost_data/i18n/zh_cn_tw/_source/story.json")

    data_story_bond = i18nFileLoader(r"../../ost_data/i18n", ["zh_cn_cn", "zh_cn_jp", "zh_cn_tw", "zh_tw"],
                                     "story_bond.json")
    data_story_bond.set_original_filepath(r"../ost_data/i18n/zh_cn_tw/_source/story_bond.json")

    data_story_all = i18nFileLoader(r"../../ost_data/i18n", ["zh_cn_cn", "zh_cn_jp", "zh_cn_tw", "zh_tw"],
                                    "story_all.json")
    data_story_all.set_original_filepath(r"../ost_data/i18n/zh_cn_tw/_source/story_all.json")

    all_data = [data_story, data_story_bond, data_story_all]
    for i in all_data:
        i.add_converters(*ALL_CONVERTER)
        i.normalize_origin_file()
        i.convert_and_write()


if __name__ == "__main__":
    convert_ost_data()

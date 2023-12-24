import json
from collections import OrderedDict

__all__ = ["ParserTool", "i18nPool", "DataProcessTool"]


class ParserTool:
    @staticmethod
    def str_list_auto_strip(str_list: list) -> list[str, ...]:
        temp = str_list.copy()
        for i in range(len(temp)):
            temp[i] = temp[i].strip()
        return temp

    @staticmethod
    def _str_split_to_list(string: str) -> list[str, ...]:
        if "," in string:
            # 逗号分隔
            result = string.split(",")
        else:
            result = string.split(" ")
        result = ParserTool.str_list_auto_strip(result)
        return result

    @staticmethod
    def str_bool_list_split(str_list: str) -> list[bool]:
        temp = ParserTool._str_split_to_list(str_list)
        result = []

        for i in temp:
            if i == "True" or i == "T":
                result.append(True)
            elif i == "False" or i == "F":
                result.append(False)
            else:
                raise ValueError(f"Unknown bool string: {i}")

        return result

    @staticmethod
    def str_str_list_split(str_list: str) -> list[str]:
        return ParserTool._str_split_to_list(str_list)

    @staticmethod
    def storyinfo_source_list_split(str_list: str) -> list:
        result = ParserTool._str_split_to_list(str_list)
        return [result[0], int(result[1]), result[2], result[3]]

    @staticmethod
    def storypart_source_list_split(str_list: str) -> list:
        result = ParserTool._str_split_to_list(str_list)
        return [result[0], int(result[1]) - 1, result[2]]

    @staticmethod
    def punc_normalize(string: str) -> str:
        conversion = {
            "-": ["\u2014", "\u2013", "\uff0d"],
            "/": ["\uff0f"],
            ",": ["\uff0c"],
            "|": ["\uff5c"],
            ";": ["\uff1b"],
            ":": ["\uff1a"]
        }

        temp = string
        for (key, value) in conversion.items():
            for i in value:
                temp.replace(i, key)

        return temp


class i18nPool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(i18nPool, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.data = OrderedDict()

    def add(self, key, value) -> None:
        self.data[key] = value

    def remove(self, key) -> str:
        return self.data.pop(key)

    def to_json(self, filepath: str, encoding: str = "utf-8"):
        with open(filepath, mode="w", encoding=encoding) as file:
            json.dump(self.data, file, indent=2, ensure_ascii=False)

    @staticmethod
    def get_i18n_key(header: str, part_num: str or int = -1, seg_num: str or int = -1,
                     type: int = -1, other_params: list = None) -> str:
        """type = 1, NAME; type = 2, DESC"""
        if other_params is None:
            other_params = []

        temp = [header]

        if part_num != -1:
            temp.append("P" + str(part_num))
            if seg_num != -1:
                temp.append("S" + str(seg_num))

        temp.append("NAME" if type == 1 else "DESC")
        temp.extend(other_params)

        return "[" + "_".join(temp) + "]"

    @staticmethod
    def get_storyinfo_i18n_header(pos_dict: dict, filetype: int) -> str:
        storytype_dict = {
            11: "MAIN", 12: "SIDE", 13: "SHORT",
            14: "EVENT", 15: "BOND", 16: "OTHER"
        }

        temp = ["STORY", storytype_dict[filetype]]
        if filetype in [11, 12, 13, 16]:
            temp.append(pos_dict["volume"])
            temp.append(pos_dict["chapter"])
            temp.append(pos_dict["segment"])
        elif filetype == 15:
            temp.append(pos_dict["student"].upper())
            temp.append(pos_dict["segment"])
        elif filetype == 14:
            temp.append(pos_dict["event_id"])
            temp.append(pos_dict["segment"])

        return "_".join([str(i) for i in temp])


class DataProcessTool:
    @staticmethod
    def storypart_source_to_dict(part_source: list, info_source: dict):
        """
        自动生成StoryPartSource dict

        :param part_source: 一个list，当前所有source（经storypart_source_list_split切割）
        :param info_source: 一个StoryInfoSource dict
        :return: StoryPartSource dict
        """
        part_source_dict = {}

        # 复制一个info_source出来
        for (key, value) in info_source.items():
            part_source_dict[key] = []

            for entry in value:
                if entry["platform"] in [2, 3]:
                    # 视频网站
                    part_source_dict[key].append({"timestamp": 0})
                elif entry["platform"] == 4:
                    # 剧情站
                    part_source_dict[key].append({"script_index": 0})
                else:
                    raise ValueError(f"Unknown platform {entry['platform']}")

        # 读取内容
        for entry in part_source:
            lang, pos, value = entry[0], entry[1], entry[2]
            if info_source[lang][pos]["platform"] in [2, 3]:
                timestamp = part_source_dict[lang][pos]["timestamp"]
                try:
                    timestamp = int(timestamp)
                except ValueError:
                    timestamp = ParserTool.punc_normalize(timestamp).split(":")
                    timestamp = int(timestamp[0]) * 60 + int(timestamp[1])

                # 视频网站
                part_source_dict[lang][pos]["timestamp"] = timestamp
            elif info_source[lang][pos]["platform"] == 4:
                # 剧情站
                part_source_dict[lang][pos]["script_index"] = int(value)

        return part_source_dict

    @staticmethod
    def storypos_to_dict(pos_list: list, filetype: int) -> dict:
        if filetype in [11, 12, 13, 16]:
            try:
                volume = int(pos_list[0])
            except ValueError:
                volume = pos_list[0]

            return {"volume": volume,
                    "chapter": int(pos_list[1]),
                    "segment": int(pos_list[2])}
        elif filetype == 15:
            return {"student": pos_list[0],
                    "segment": int(pos_list[1])}
        elif filetype == 14:
            return {"event_id": int(pos_list[0]),
                    "segment": int(pos_list[1])}
        else:
            raise ValueError(f"Unknown filetype {filetype}")

    @staticmethod
    def storypart_params_to_dict(params_list: list, filetype: int) -> dict:
        if filetype == 15:
            return {"is_memory": params_list[0],
                    "is_momotalk": params_list[1]}
        else:
            return {"is_battle": params_list[0]}

    @staticmethod
    def storyinfo_source_to_dict(source_list: list) -> dict:
        story_source_dict = {"en": [], "zh_tw": [],
                             "zh_cn_cn": [], "zh_cn_jp": []}

        for entry in source_list:
            lang, platform, url, i18n_text = entry[0], entry[1], entry[2], entry[3]
            story_source_dict[lang].append({"platform": int(platform),
                                            "value": url,
                                            "short_desc": i18n_text})

        return story_source_dict

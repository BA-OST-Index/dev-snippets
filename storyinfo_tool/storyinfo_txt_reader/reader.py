import uuid
import os
import opencc
from .tool import *
from .file_tool import FileReader

I18N = i18nPool()
TW_TO_CN = opencc.OpenCC("tw2sp.json")


class StoryInfoTxtReader:
    def __init__(self, file_reader: FileReader):
        self.file_reader = file_reader
        self.special_story = False
        if self.file_reader.last_read_autoflag != ";;":
            raise ValueError

        print("reading", file_reader.filepath)
        self.storyinfo_basic()

    def storyinfo_basic(self):
        self.uuid = self.file_reader.readline()
        if self.uuid == "" or self.uuid == "[UUID_AUTO]":
            self.uuid = str(uuid.uuid4())
            self.file_reader.add_rewrite_content(self.uuid)

        self.filetype = int(self.file_reader.readline())
        self.pos = DataProcessTool.storypos_to_dict(
            ParserTool.str_str_list_split(self.file_reader.readline()),
            self.filetype
        )
        self.i18n_header = I18N.get_storyinfo_i18n_header(self.pos, self.filetype)

        # 注意这里是先归化成了简中，因为之后i18n导出时会专门转繁
        title = TW_TO_CN.convert(self.file_reader.readline())
        I18N.add(I18N.get_i18n_key(self.i18n_header, -1, -1, 1), title)

        desc = []
        _counter = 1
        while True:
            self.file_reader.readline()
            if self.file_reader.last_read_is_flag:
                break

            I18N.add(I18N.get_i18n_key(self.i18n_header, -1, -1, 2, [str(_counter)]),
                     TW_TO_CN.convert(self.file_reader.last_read))  # 注意这里是先归化成了简中，因为之后i18n导出时会专门转繁
            desc.append(I18N.get_i18n_key(self.i18n_header, -1, -1, 2, [str(_counter)]))
            _counter += 1

        self.info_source = self.storyinfo_source()

        story_parts = []
        _counter = 1
        while True:
            if self.file_reader.last_read_is_flag:
                if self.file_reader.last_read_autoflag == "--":
                    story_parts.append(self.storypart_basic(_counter))
                    _counter += 1
                    continue
                elif self.file_reader.last_read_autoflag == ";;":
                    # 第二次读到这个，终止本StoryInfo读取
                    break
            self.file_reader.readline()

        json_result = {
            "uuid": self.uuid,
            "filetype": self.filetype,
            "name": I18N.get_i18n_key(self.i18n_header, -1, -1, 1),
            "desc": desc,
            "pos": self.pos,
            "image": {
                "platform": -1,
                "value": "",
                "short_desc": ""
            },
            "source": self.info_source,
            "part": story_parts
        }
        if self.filetype == 15:
            json_result["is_memory"] = self.special_story
        else:
            json_result["is_battle"] = self.special_story

        self.json_result = json_result

    def storyinfo_source(self) -> dict:
        result = {"en": [], "zh_tw": [], "zh_cn_cn": [], "zh_cn_jp": []}

        # if not the expected flag, return an empty dict
        if self.file_reader.last_read_autoflag != "||":
            return result

        data = []
        while True:
            self.file_reader.readline()
            if self.file_reader.last_read_is_flag:
                break

            data.append(ParserTool.storyinfo_source_list_split(self.file_reader.last_read))

        for i in data:
            lang, platform, url, i18n_text = i[0], i[1], i[2], i[3]
            result[lang].append({"platform": int(platform),
                                 "value": url,
                                 "short_desc": i18n_text})

        return result

    def storypart_basic(self, part_no: int) -> dict:
        if self.file_reader.last_read_autoflag != "--":
            raise ValueError

        json_result = {
            "name": "",
            "source": {},
            "data": []
        }

        name = self.file_reader.readline()
        I18N.add(I18N.get_i18n_key(self.i18n_header, part_no, -1, 1), name)
        json_result["name"] = I18N.get_i18n_key(self.i18n_header, part_no, -1, 1)

        json_result.update(DataProcessTool.storypart_params_to_dict(
            ParserTool.str_bool_list_split(self.file_reader.readline()),
            self.filetype
        ))
        if self.filetype == 15:
            if json_result["is_memory"]:
                self.special_story = True
        elif json_result["is_battle"]:
            self.special_story = True

        json_result["source"] = self.storypart_source()

        seg_data = []
        _counter = 1
        while True:
            if self.file_reader.last_read_autoflag == "//":
                seg_data.append(self.storyseg_basic(part_no, _counter))
                _counter += 1

            self.file_reader.readline()

            if self.file_reader.last_read_autoflag != "//":
                break

        json_result["data"] = seg_data

        return json_result

    def storypart_source(self) -> dict:
        self.file_reader.readline()
        if self.file_reader.last_read_autoflag != "||":
            # 全部的seg source数据都返回默认值
            # 如 视频timestamp=0 剧情站script_index=0
            return DataProcessTool.storypart_source_to_dict([], self.info_source)

        data = []
        while True:
            self.file_reader.readline()
            if self.file_reader.last_read_autoflag == "//":
                break

            data.append(ParserTool.storypart_source_list_split(self.file_reader.last_read))

        return DataProcessTool.storypart_source_to_dict(data, self.info_source)

    def storyseg_basic(self, part_no: int, seg_no: int) -> dict:
        if self.file_reader.last_read_autoflag != "//":
            raise ValueError

        desc = self.file_reader.readline()
        I18N.add(I18N.get_i18n_key(self.i18n_header, part_no, seg_no, 2), desc)
        chars = ParserTool.str_str_list_split(self.file_reader.readline())
        tracks = ParserTool.str_str_list_split(self.file_reader.readline())
        backgrounds = ParserTool.str_str_list_split(self.file_reader.readline())

        json_result = {
            "desc": I18N.get_i18n_key(self.i18n_header, part_no, seg_no, 2),
            "character": [] if chars[0] == "" else chars,
            "track": [] if tracks[0] == "" else tracks,
            "background": [] if backgrounds[0] == "" else backgrounds
        }

        return json_result

    @property
    def filepath(self) -> str:
        storytype_dict = {
            11: "main", 12: "side", 13: "short",
            14: "event", 15: "bond", 16: "other"
        }

        if self.filetype in [11, 12, 13, 16]:
            temp = ["main", "story", storytype_dict[self.filetype],
                    str(self.pos["volume"]), str(self.pos["chapter"])]
        elif self.filetype == 15:
            temp = ["character", "student", self.pos["student"], "bond"]
        else:
            temp = ["event", str(self.pos["event_id"]), "story"]

        temp.append(str(self.pos["segment"]).rjust(2, "0") + ".json")
        temp = "/".join(temp)

        return os.path.normpath(temp)

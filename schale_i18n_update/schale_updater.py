import requests
import json
import opencc

URL_FORMAT = "https://github.com/lonqie/SchaleDB/raw/main/data/{lang}/{filename}"
PATH_FORMAT = r"../ost_data/i18n/{lang}/schale/{filename}"
LANG_LIST = ["cn", "zh", "tw", "jp", "en", "th", "kr"]
LANG_BOI_LIST = ["zh_cn_cn", "zh_cn_jp", "zh_tw", "jp", "en", "thai", "kr"]
TW_TO_CN = opencc.OpenCC("tw2sp.json")
get_json = lambda url: requests.get(url).json()


def json_extract(filename, data):
    if filename == "localization.json":
        keys = ["School", "SchoolLong", "Club", "BossFaction", "EventName", "StageType", "TimeAttackStage",
                "ConquestMap", "StageTitle", "SquadType", "BulletType", "ArmorType"]
        return {key + "_" + key_2: data[key][key_2] for key in keys for key_2 in data[key]}

    if filename == "students.json":
        keys = ["Id", "PathName", "DevName", "FamilyName", "PersonalName", "SchoolYear", "CharacterAge", "Birthday",
                "CharacterSSRNew", "ProfileIntroduction", "Hobby", "BirthDay", "School", "Club", "CollectionBG", "Name",
                "SquadType", "BulletType", "ArmorType"]
        d = {dict_["PathName"]: {key: dict_[key] for key in keys} for dict_ in data}
        for i in d.values():
            for j, k in i.items():
                if k is None:
                    i[j] = "None"

        return d
    elif filename == "raids.json":
        keys = ["PathName", "Faction", "Name", "Profile"]
    else:
        keys = []
    return {dict_["PathName"]: {key: dict_[key] for key in keys} for dict_ in data}


json_student = {lang: get_json(URL_FORMAT.format(lang=lang, filename="students.json")) for lang in LANG_LIST}
json_localization = {lang: get_json(URL_FORMAT.format(lang=lang, filename="localization.json")) for lang in LANG_LIST}
json_raid = {lang: get_json(URL_FORMAT.format(lang=lang, filename="raids.json")) for lang in LANG_LIST}

for (i, j) in zip(LANG_LIST, LANG_BOI_LIST):
    with open(PATH_FORMAT.format(lang=j, filename="students.json"), mode="w", encoding="UTF-8") as file:
        json.dump(json_extract("students.json", json_student[i]), file,
                  ensure_ascii=False, indent=2)
    with open(PATH_FORMAT.format(lang=j, filename="localization.json"), mode="w", encoding="UTF-8") as file:
        json.dump(json_extract("localization.json", json_localization[i]), file,
                  ensure_ascii=False, indent=2)
    with open(PATH_FORMAT.format(lang=j, filename="raids.json"), mode="w", encoding="UTF-8") as file:
        json.dump(json_extract("raids.json", json_raid[i]["Raid"]), file,
                  ensure_ascii=False, indent=2)

# zh_cn_tw
with open(PATH_FORMAT.format(lang="zh_cn_tw", filename="students.json"), mode="w", encoding="UTF-8") as file:
    temp = json.dumps(json_extract("students.json", json_student["tw"]), ensure_ascii=False, indent=2)
    temp = TW_TO_CN.convert(temp)
    file.write(temp)
with open(PATH_FORMAT.format(lang="zh_cn_tw", filename="localization.json"), mode="w", encoding="UTF-8") as file:
    temp = json.dumps(json_extract("localization.json", json_localization["tw"]), ensure_ascii=False, indent=2)
    temp = TW_TO_CN.convert(temp)
    file.write(temp)
with open(PATH_FORMAT.format(lang="zh_cn_tw", filename="raids.json"), mode="w", encoding="UTF-8") as file:
    temp = json.dumps(json_extract("raids.json", json_raid["tw"]["Raid"]), ensure_ascii=False, indent=2)
    temp = TW_TO_CN.convert(temp)
    file.write(temp)

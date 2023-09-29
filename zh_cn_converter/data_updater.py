import requests
import json
import opencc
from collections import namedtuple


# -----------------General Function-----------------
def load_json(url):
    return requests.get(url).json()


ZhI18nData = namedtuple("ZhI18nData", ["zh_cn_jp", "zh_cn_cn", "zh_cn_tw", "zh_tw"])
TwToCn = opencc.OpenCC("tw2sp.json")
# --------------------------------------------------

i18n_students = ["https://github.com/lonqie/SchaleDB/raw/main/data/cn/students.json",
                 "https://github.com/lonqie/SchaleDB/raw/main/data/zh/students.json",
                 "https://github.com/lonqie/SchaleDB/raw/main/data/tw/students.json",
                 "https://github.com/lonqie/SchaleDB/raw/main/data/jp/students.json"]
i18n_localization = ["https://github.com/lonqie/SchaleDB/raw/main/data/cn/localization.json",
                     "https://github.com/lonqie/SchaleDB/raw/main/data/zh/localization.json",
                     "https://github.com/lonqie/SchaleDB/raw/main/data/tw/localization.json",
                     "https://github.com/lonqie/SchaleDB/raw/main/data/jp/localization.json"]
i18n_raid = ["https://github.com/lonqie/SchaleDB/raw/main/data/cn/raids.json",
             "https://github.com/lonqie/SchaleDB/raw/main/data/zh/raids.json",
             "https://github.com/lonqie/SchaleDB/raw/main/data/tw/raids.json",
             "https://github.com/lonqie/SchaleDB/raw/main/data/jp/raids.json"]

json_students = [load_json(i) for i in i18n_students]
json_localization = [load_json(i) for i in i18n_localization]
json_raid = [load_json(i) for i in i18n_raid]

# ----------------- Student Data -----------------
# first name, last name
data_student_firstname = []
data_student_lastname = []
for (cn, zh, tw, jp) in zip(*json_students):
    tw_lastname = TwToCn.convert(tw["FamilyName"]) if tw["FamilyName"] != jp["FamilyName"] else zh["FamilyName"]
    data_student_lastname.append(ZhI18nData(zh["FamilyName"], cn["FamilyName"], tw_lastname, tw["FamilyName"]))
    tw_firstname = TwToCn.convert(tw["PersonalName"]) if tw["PersonalName"] != jp["PersonalName"] else zh[
        "PersonalName"]
    data_student_firstname.append(ZhI18nData(zh["PersonalName"], cn["PersonalName"], tw_firstname, tw["PersonalName"]))


# ----------------- LocalizationData -----------------
# club name, school name (short/long), boss faction
def get_data_by_keyname(dataset, first_key_name):
    temp = []
    for keyname in dataset[3][first_key_name].keys():
        cn = json_localization[0][first_key_name][keyname]
        zh = json_localization[1][first_key_name][keyname]
        tw = json_localization[2][first_key_name][keyname]
        if tw == json_localization[3][first_key_name][keyname]:
            tw = tw_zh = cn
        else:
            tw_zh = TwToCn.convert(tw)
        temp.append(ZhI18nData(cn, zh, tw_zh, tw))
    return temp


data_l10n_club = get_data_by_keyname(json_localization, "Club")
data_l10n_school_short = get_data_by_keyname(json_localization, "School")
data_l10n_school_long = get_data_by_keyname(json_localization, "SchoolLong")
data_l10n_boss_faction = get_data_by_keyname(json_localization, "BossFaction")

# ----------------- RaidData -----------------
# total_assault, world raid
data_raid_total_assault = []
data_raid_world_raid = []
for (cn, zh, tw, jp) in zip(json_raid[0]["Raid"], json_raid[1]["Raid"], json_raid[2]["Raid"], json_raid[3]["Raid"]):
    tw_name = TwToCn.convert(tw["Name"]) if tw["Name"] != jp["Name"] else zh["Name"]
    data_raid_total_assault.append(ZhI18nData(cn["Name"], zh["Name"], tw_name, tw["Name"]))
for (cn, zh, tw, jp) in zip(json_raid[0]["WorldRaid"], json_raid[1]["WorldRaid"],
                            json_raid[2]["WorldRaid"], json_raid[3]["WorldRaid"]):
    tw_name = TwToCn.convert(tw["Name"]) if tw["Name"] != jp["Name"] else zh["Name"]
    data_raid_world_raid.append(ZhI18nData(cn["Name"], zh["Name"], tw_name, tw["Name"]))

# ----------------- WriteData -----------------
def write_json(dataset: list[ZhI18nData, ...], filepath):
    temp = []
    for i in dataset:
        temp.append([i.zh_cn_jp, i.zh_cn_cn, i.zh_cn_tw, i.zh_tw])
    with open(filepath, mode="w", encoding="UTF-8") as file:
        json.dump(temp, file, ensure_ascii=False, indent=2)


write_json(data_student_firstname, "data/stu_first.json")
write_json(data_student_lastname, "data/stu_last.json")
write_json(data_l10n_club, "data/l10n_club.json")
write_json(data_l10n_boss_faction, "data/l10n_boss_faction.json")
write_json(data_l10n_school_short, "data/l10n_school_short.json")
write_json(data_l10n_school_long, "data/l10n_school_long.json")
write_json(data_raid_total_assault, "data/raid_total.json")
write_json(data_raid_world_raid, "data/raid_world.json")

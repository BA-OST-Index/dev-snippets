import os
import uuid
import json

DATA_PATH = "ost_data/background"

ori_backgrounds = set(os.listdir(r"E:\com.nexon.bluearchive\files\PUB\Resource\GameData\MediaResources\UIs"
                                 r"\03_Scenario\01_Background"))
preload_backgrounds = set(os.listdir(r"E:\com.nexon.bluearchive\files\PUB\Resource\Preload\MediaResources\UIs"
                                     r"\03_Scenario\01_Background"))
all_backgrounds = ori_backgrounds.union(preload_backgrounds)

temp = []
for i in all_backgrounds:
    if i.endswith("_kr.jpg"):
        temp.append(i)
for i in temp:
    all_backgrounds.remove(i)

for i in all_backgrounds:
    # if files exist, don't touch it
    if os.path.isfile(os.path.join(DATA_PATH, i)):
        continue

    data = {
        "uuid": str(uuid.uuid4()),
        "filetype": 71,
        "filename": i,
        "name": f"[{i}_NAME]",
        "desc": f"[{i}_DESC]",

        "tag": [],

        "image": {
            "platform": -1,
            "value": f"/static/images/background/{i}",
            "short_desc": ""
        }
    }
    with open(f"generated/background/{i}.json", mode="w", encoding="UTF-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

import os.path
import json
import uuid
from collections import OrderedDict

# Config
INPUT_FILE = "yuuka.txt"
OUTPUT_DIR = "output"
STORY_TYPE = "MAIN"
JSON_FILETYPE = "11"

# 依序读取所有内容
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    VOLUME = int(file.readline().strip())
    CHAPTER = int(file.readline().strip())
    EPISODES = file.read().split("\n\n")
STORY_PARTS = []
for ep in EPISODES:
    temp = []
    content = ep.split("\n")
    temp.append(content[0])
    for i in range(1, len(content), 2):
        temp.append((content[i].strip(), content[i + 1].strip()))
    STORY_PARTS.append(temp)

# story.json
# 默认是MAIN
STORY_NAME = f"[STORY_{STORY_TYPE}_{VOLUME}_{CHAPTER}_[NO]_NAME]"
STORY_DESC = f"[STORY_{STORY_TYPE}_{VOLUME}_{CHAPTER}_[NO]_DESC]"
STORY_PART_NAME = f"[STORY_{STORY_TYPE}_{VOLUME}_{CHAPTER}_[NO]_P[PNO]_NAME]"
STORY_PART_DESC = f"[STORY_{STORY_TYPE}_{VOLUME}_{CHAPTER}_[NO]_P[PNO]_DESC]"
STORYPART_DATA = OrderedDict()
for story in STORY_PARTS:
    story_no = int(story[0])
    STORYPART_DATA[STORY_NAME.replace("[NO]", str(story_no))] = ""
    STORYPART_DATA[STORY_DESC.replace("[NO]", str(story_no))] = ""
    for (no, (title, desc)) in enumerate(story[1:], 1):
        STORYPART_DATA[STORY_PART_NAME.replace("[NO]", str(story_no)).replace("[PNO]", str(no))] = title
        STORYPART_DATA[STORY_PART_DESC.replace("[NO]", str(story_no)).replace("[PNO]", str(no))] = desc

os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(os.path.join(OUTPUT_DIR, "output_story.json"), "w", encoding="UTF-8") as file:
    json.dump(STORYPART_DATA, file, indent=2, ensure_ascii=False)

# JSON
JSON_FORMAT = """{
  "uuid": "[UUID]",
  "filetype": [FILETYPE],

  "name": "[STORY_NAME]",
  "desc": "[STORY_DESC]",
  "pos": {
    "volume": [STORY_VOLUME],
    "chapter": [STORY_CHAPTER],
    "segment": [STORY_SEGMENT]
  },
  "image": {
    "platform": -1,
    "value": "",
    "short_desc": ""
  },

  "part": [
[STORY_PARTS]
  ],
  "is_battle": false
}"""
JSON_PART_FORMAT = """    {
      "name": "[STORY_NAME]",
      "desc": "[STORY_DESC]",
      "is_battle": false,
      "track": [],
      "background": [],
      "character": []
    }"""

JSON_DATA = []
for no, story in enumerate(STORY_PARTS, 1):
    story_no = int(story[0])
    json_content = JSON_FORMAT.replace("[UUID]", str(uuid.uuid4())). \
        replace("[STORY_NAME]", str(STORY_NAME.replace("[NO]", str(story_no)))). \
        replace("[STORY_DESC]", str(STORY_DESC.replace("[NO]", str(story_no)))). \
        replace("[STORY_VOLUME]", str(VOLUME)). \
        replace("[STORY_CHAPTER]", str(CHAPTER)). \
        replace("[STORY_SEGMENT]", str(story_no)). \
        replace("[FILETYPE]", str(JSON_FILETYPE))

    parts = []
    for i in range(1, len(story)):
        parts.append(JSON_PART_FORMAT.replace("[STORY_NAME]",
                                              STORY_PART_NAME.replace("[NO]", str(story_no))
                                              .replace("[PNO]", str(no)))
                     .replace("[STORY_DESC]", STORY_PART_NAME.replace("[NO]", str(story_no))
                              .replace("[PNO]", str(no))))

    json_content = json_content.replace("[STORY_PARTS]", ",\n".join(parts[:-1]) + parts[-1])
    JSON_DATA.append(json_content)

os.makedirs(os.path.join(OUTPUT_DIR, "story"), exist_ok=True)
for (no, content) in enumerate(JSON_DATA, 1):
    with open(os.path.join(OUTPUT_DIR, "story", f"{no}.json".zfill(7)), "w", encoding="utf-8") as file:
        file.write(content)

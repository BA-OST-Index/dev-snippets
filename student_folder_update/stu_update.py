import requests
import os
import uuid

STU_ROOT_FILE_JSON = '''{
  "uuid": "[UUID_REPLACE]",
  "filetype": -53,
  "namespace": "[NAMESPACE_REPLACE]",
  "name": "[NAME_REPLACE]",
  "desc": "",
  "include": [
    "[AUTO]"
  ]
}'''
STU_BOND_FILE_JSON = '''{
  "uuid": "[UUID_REPLACE]",
  "filetype": -54,
  "name": "",
  "namespace": "bond",
  "desc": "",
  "include": [
    "[AUTO]"
  ]
}'''
DATA_PATH = "../ost_data/character/student"

r = requests.get("https://raw.githubusercontent.com/lonqie/SchaleDB/main/data/en/students.json")
r = r.json()

all_student_pathname = [i["PathName"] for i in r]
all_existed_pathname = []
for i in os.listdir(DATA_PATH):
    if os.path.isdir(os.path.join(DATA_PATH, i)):
        all_existed_pathname.append(i)
all_non_existed_pathname = list(set(all_student_pathname) - set(all_existed_pathname))
print(all_non_existed_pathname)

for i in all_non_existed_pathname:
    print("to create", i)

    # create folder
    os.makedirs(os.path.join(DATA_PATH, f"{i}/bond"), exist_ok=True)

    with open(os.path.join(DATA_PATH, f"{i}/_all.json"), mode="w", encoding="UTF-8") as file:
        file.write(STU_ROOT_FILE_JSON.replace("[UUID_REPLACE]", str(uuid.uuid4())).
                   replace("[NAMESPACE_REPLACE]", i.lower()).replace("[NAME_REPLACE]", i))
    with open(os.path.join(DATA_PATH, f"{i}/bond/_all.json"), mode="w", encoding="UTF-8") as file:
        file.write(STU_BOND_FILE_JSON.replace("[UUID_REPLACE]", str(uuid.uuid4())))

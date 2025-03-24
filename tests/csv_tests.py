# This script builds language files from CSV translation files.

import csv
import glob
import pathlib
import re

# An Exception containing all errors and warnings found during building.
class ProcessException(RuntimeError):
    def __init__(self,message,errors, warnings):
        super().__init__(message)
        self.errors = errors
        self.warnings = warnings

# Load the English file as a base to build translation files from.
def load_english():
    contents = []

    with open('language.txt', 'r', encoding="utf8") as topo_file:
        data = topo_file.read()

    for line in data.splitlines():
        matches = re.search(r"^([a-zA-Z0-9_+]+)(\s+)(.+)$", line)
        if matches == None:
            contents.append(line)
        else:
            contents.append(matches.groups())

    return contents

english = load_english()

def load_language(translation_file):
    language = []
    headers = []
    header = False
    csv_reader = csv.reader(translation_file, delimiter=',')
    for row in csv_reader:
        if not header:
            headers = row
            header = True
        else:
            if len(headers) == len(row):
                item = {}
                for idx, data in enumerate(row):
                    item[headers[idx]] = data
                language.append(item)
            else:
                print("CSVError:", row[headers.index('key')])

    return language

def get_language_strings(language):
    strings = {}
    for line in language:
        if line['key'] in strings.keys():
            print("DuplicateError:", line['key'])
        strings[line['key']] = line['translation']
    return strings

def fix_language_file(language):
    strings = get_language_strings(language)

    output = []
    for line in english:
        if isinstance(line, tuple):
            try:
                if strings[line[0]] == "#ERROR!":
                    print("ExcelError:", line[0])
                output.append(line[0] + line[1] + strings[line[0]])
            except KeyError as ex:
                print("KeyError: Couldn't locate " + line[0])
                output.append(line[0] + line[1] + line[2])
        else:
            output.append(line)

    return output

for file in glob.glob('data/language/**/language.csv', recursive=True):
    print()
    print("Processing", file)
    print("=======================================================")
    dir = pathlib.Path(file).parents[0]
    name = pathlib.Path(file).stem
    pathlib.Path("../latest/"+str(dir)).mkdir(parents=True, exist_ok=True)

    language = None
    with open (file, 'r', encoding="utf8") as translation_file:
        language = load_language(translation_file)
    fixed = fix_language_file(language)

    # print("Writing ../latest/"+str(dir)+"/"+name+".txt")
    # with open("../latest/"+str(dir)+"/"+name+".txt", 'w', encoding="utf8") as language_file:
        # for line in fixed:
            # language_file.write(f"{line}\n")
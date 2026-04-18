#!/usr/bin/python3
import os
import sys
import json
import bz2


def compile_db(db_console_name):
    db = {}
    print(f"Compiling cheat code db for {db_console_name}...")

    if 'switch' in db_console_name:
        for root, _, files in os.walk('./switch'):
            root = root.replace('\\', '/')
            titleid = root[root.rfind('/') + 1:]

            if "switch" in titleid:
                continue

            db[titleid] = {}
            for file in files:
                buildid = file[:file.find('.')]
                db[titleid][buildid] = {}
                with open(os.path.join(root, file), 'r', encoding="UTF-8") as f:
                    lines = [line.strip() for line in f]
                    lines = list(filter(None, lines))
                    selectedCheat = lines[0]
                    for line in lines:
                        if line.startswith('{') and line.endswith('}'):
                            pass
                        elif line.startswith('[') and line.endswith(']'):
                            selectedCheat = line[1:-1]
                            db[titleid][buildid][selectedCheat] = []
                        else:
                            try:
                                db[titleid][buildid][selectedCheat].append(line)
                            except KeyError:
                                print(f"Error: Failed to process cheat file - titleid: {titleid}, buildid: {buildid}")
                                break
    compressed = bz2.compress(str.encode(json.dumps(db)))
    with open(os.path.join('build', db_console_name + '.json'), 'w') as f:
        f.write(json.dumps(db, indent=2))
    with open(os.path.join('build', db_console_name + '.json.bz2'), 'wb') as f:
        f.write(compressed)


if __name__ == '__main__':
    args = list(i for i in sys.argv[1:] if i in ("switch"))
    if len(sys.argv) == 1:
        args = ["switch"]
    if not args:
        input("Proper argument options is 'switch', or nothing.")
        exit(0)
    for arg in args:
        compile_db(arg)
        print(f"Wrote compiled cheat code DB to 'build/{arg}.json'.")

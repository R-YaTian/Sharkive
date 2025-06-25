#!/usr/bin/python3
import os
import sys
import json
import bz2


def compile_db(db_language_code):
    db = {}
    print(f"Compiling cheat code db for {db_language_code}...")

    dirname = ''
    if 'chs' in db_language_code:
        dirname = './3ds'
    elif 'eng' in db_language_code:
        dirname = './eng'

    for cheat in os.listdir(dirname):
        with open(os.path.join(dirname, cheat), 'r', encoding="UTF-8") as file:
            titleid = cheat[:cheat.rfind('.')]
            lines = [line.strip() for line in file]
            lines = list(filter(None, lines))

            db[titleid] = {}
            selectedCheat = lines[0]
            for line in lines:
                if line.startswith('{') and line.endswith('}'):
                    pass
                elif line.startswith('[') and line.endswith(']'):
                    selectedCheat = line[1:-1]
                    db[titleid][selectedCheat] = []
                else:
                    db[titleid][selectedCheat].append(line)

    compressed = bz2.compress(str.encode(json.dumps(db)))
    with open(os.path.join('build', '3ds_' + db_language_code + '.json'), 'w') as f:
        f.write(json.dumps(db))
    with open(os.path.join('build', '3ds_' + db_language_code + '.json.bz2'), 'wb') as f:
        f.write(compressed)


if __name__ == '__main__':
    args = list(i for i in sys.argv[1:] if i in ("chs", "eng"))
    if len(sys.argv) == 1:
        args = ["chs", "eng"]
    if not args:
        print("Proper argument options are 'chs' or 'eng', or nothing to compile both.")
        exit(0)
    for arg in args:
        compile_db(arg)
        print(f"Wrote compiled cheat code DB to 'build/3ds_{arg}.json'.")

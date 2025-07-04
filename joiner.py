#!/usr/bin/python3
import os
import sys
import json
import threading
import zipfile
try:
    import zopfli
except ImportError:
    print("Python: zopfli library not found. Please install zopflipy.")
    print("\tYou can install it using: pip install zopflipy")
    raise SystemExit(1)


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

    json_str = json.dumps(db)
    json_data = json_str.encode()
    json_path = os.path.join('build', '3ds_' + db_language_code + '.json')
    zip_path = json_path + '.zip'

    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_str)

    with zopfli.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as f:
        f.writestr(os.path.basename(json_path), json_data)

def compile_and_print(arg):
    compile_db(arg)
    print(f"Wrote compiled cheat code DB to 'build/3ds_{arg}.json'.")


if __name__ == '__main__':
    args = list(i for i in sys.argv[1:] if i in ("chs", "eng"))
    if len(sys.argv) == 1:
        args = ["chs", "eng"]
    if not args:
        print("Proper argument options are 'chs' or 'eng', or nothing to compile both.")
        exit(0)

    threads = []

    for arg in args:
        t = threading.Thread(target=compile_and_print, args=(arg,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

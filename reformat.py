"""Add blank lines between cheat sections for cheats TXT file."""

from pathlib import Path
import re


HEADER = re.compile(rb"[ \t]*(?:\[[^\r\n]*\]|\{[^\r\n]*\})[ \t]*")
LINE_END = re.compile(rb"\r\n|\n|\r")
UTF8_BOM = b"\xef\xbb\xbf"


def reformat(data: bytes) -> bytes:
    bom = UTF8_BOM if data.startswith(UTF8_BOM) else b""
    lines = data[len(bom):].splitlines(keepends=True)
    if not lines:
        return data

    first_end = LINE_END.search(data)
    newline = first_end.group() if first_end else b"\r\n"
    output = []
    for line in lines:
        if (
            output
            and output[-1].strip()
            and HEADER.fullmatch(line.rstrip(b"\r\n"))
        ):
            output.append(newline)
        output.append(line)
        end = LINE_END.search(line)
        if end:
            newline = end.group()

    return bom + b"".join(output)


def main() -> None:
    titles = Path(__file__).resolve().parent / "titles"
    if not titles.is_dir():
        raise SystemExit(f"Directory not found: {titles}")

    scanned = updated = 0
    unchanged = []
    for path in titles.rglob("*.txt"):
        if not path.is_file():
            continue
        original = path.read_bytes()
        formatted = reformat(original)
        scanned += 1
        if formatted != original:
            path.write_bytes(formatted)
            updated += 1
        else:
            unchanged.append(path)
    print(f"Scanned {scanned} TXT files, updated {updated}, unchanged {len(unchanged)}.")
    if unchanged:
        print("Unchanged files:")
        for path in sorted(unchanged):
            print(path)


if __name__ == "__main__":
    main()

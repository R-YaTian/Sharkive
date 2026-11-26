"""Reformat cheat titles, section spacing, code words spacing and remove BOM in TXT files."""

from pathlib import Path
import re


HEADER = re.compile(rb"[ \t]*(\[[^]\r\n]*\]|\{[^}\r\n]*\})")
CODE_LINE = re.compile(rb"([ \t]*)([0-9A-Fa-f]{8}(?:[ \t]+[0-9A-Fa-f]{8})+)([ \t]*)")
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
        body = line.rstrip(b"\r\n")
        has_end = len(body) < len(line)
        if header := HEADER.match(body):
            if output and output[-1].strip():
                output.append(newline)
            body = header[1]
        elif code := CODE_LINE.fullmatch(body):
            leading, words, trailing = code.groups()
            body = leading + b" ".join(words.split()) + trailing
        output.append(body + (newline if has_end else b""))

    if output[-1].strip():
        if not output[-1].endswith(newline):
            output.append(newline)

    return b"".join(output)


def main() -> None:
    titles = Path(__file__).resolve().parent / "titles"
    if not titles.is_dir():
        raise SystemExit(f"Directory not found: {titles}")

    for title_dir in titles.iterdir():
        if title_dir.is_dir() and len(title_dir.name) != 16:
            msg = f"Warning: Folder '{title_dir.name}' length is not 16 characters"
            print(msg)

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


if __name__ == "__main__":
    main()

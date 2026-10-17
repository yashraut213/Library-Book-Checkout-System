import asyncio
from pathlib import Path

DATA_FILE = Path(__file__).parent / "library_data.txt"


class LibraryItem:
    def __init__(self, title, item_id):
        self.title = title
        self.item_id = item_id

    def display_info(self):
        print(f"Title: {self.title}, ID: {self.item_id}")


class Book(LibraryItem):
    def __init__(self, title, item_id, author):
        super().__init__(title, item_id)
        self.author = author

    def display_info(self):
        print(f"Title: {self.title}, ID: {self.item_id}, Author: {self.author}")


class DVD(LibraryItem):
    def __init__(self, title, item_id, duration):
        super().__init__(title, item_id)
        self.duration = int(duration)

    def display_info(self):
        print(f"Title: {self.title}, ID: {self.item_id}, Duration: {self.duration} minutes")


def read_text(path):
    # utf-8-sig also accepts a file that starts with a byte order mark
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


async def read_file_async(path):
    # Run the blocking read in a worker thread so the event loop stays free
    return await asyncio.to_thread(read_text, path)


def make_item(line):
    parts = line.strip().split(",")
    if len(parts) < 4:
        raise ValueError(f"Expected type,item_id,title,extra but got: {line!r}")
    item_type = parts[0].strip()
    item_id = parts[1].strip()
    extra = parts[-1].strip()
    # Everything between the ID and the last field is the title, commas included
    title = ",".join(parts[2:-1]).strip()
    if item_type == "Book":
        return Book(title, item_id, extra)
    if item_type == "DVD":
        return DVD(title, item_id, extra)
    raise ValueError(f"Unknown item type: {item_type!r}")


def parse_items(text):
    # splitlines() copes with both "\n" and Windows "\r\n" line endings
    return [make_item(line) for line in text.splitlines() if line.strip()]


async def main(path=DATA_FILE):
    text = await read_file_async(path)
    print("File contents:")
    print(text.rstrip())
    print()
    print("Library items:")
    for item in parse_items(text):
        item.display_info()


if __name__ == "__main__":
    asyncio.run(main())
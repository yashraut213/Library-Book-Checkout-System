import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from library import DVD, Book, LibraryItem, main, make_item, parse_items, read_file_async


def captured(func):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        func()
    return buffer.getvalue()


class TestClasses(unittest.TestCase):
    def test_library_item_display_info(self):
        item = LibraryItem("Atlas", "1")
        self.assertEqual(captured(item.display_info), "Title: Atlas, ID: 1\n")

    def test_book_display_info_adds_author(self):
        book = Book("The Hobbit", "101", "Tolkien")
        self.assertEqual(captured(book.display_info),
                         "Title: The Hobbit, ID: 101, Author: Tolkien\n")

    def test_dvd_display_info_adds_duration(self):
        dvd = DVD("Inception", "201", "148")
        self.assertEqual(captured(dvd.display_info),
                         "Title: Inception, ID: 201, Duration: 148 minutes\n")

    def test_subclasses_are_library_items(self):
        self.assertIsInstance(Book("A", "1", "B"), LibraryItem)
        self.assertIsInstance(DVD("A", "1", "90"), LibraryItem)


class TestParsing(unittest.TestCase):
    def test_make_item_book(self):
        item = make_item("Book,101,The Hobbit,Tolkien")
        self.assertIsInstance(item, Book)
        self.assertEqual((item.title, item.item_id, item.author),
                         ("The Hobbit", "101", "Tolkien"))

    def test_make_item_dvd(self):
        item = make_item("DVD,201,Inception,148")
        self.assertIsInstance(item, DVD)
        self.assertEqual(item.duration, 148)

    def test_title_with_comma(self):
        item = make_item("Book,103,Eats, Shoots and Leaves,Truss")
        self.assertEqual(item.title, "Eats, Shoots and Leaves")
        self.assertEqual(item.author, "Truss")

    def test_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            make_item("Magazine,301,Wired,May")

    def test_short_line_raises(self):
        with self.assertRaises(ValueError):
            make_item("Book,101")

    def test_parse_items_handles_crlf_and_blank_lines(self):
        items = parse_items("Book,101,The Hobbit,Tolkien\r\n\r\nDVD,201,Inception,148\r\n")
        self.assertEqual([type(i) for i in items], [Book, DVD])
        self.assertEqual(items[0].author, "Tolkien")
        self.assertEqual(items[1].duration, 148)


class TestAsyncReading(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(handle, "w", encoding="utf-8", newline="") as f:
            f.write("Book,101,The Hobbit,Tolkien\r\nDVD,201,Inception,148\r\n")

    def tearDown(self):
        os.remove(self.path)

    async def test_read_file_async_returns_contents(self):
        text = await read_file_async(self.path)
        self.assertIn("Book,101,The Hobbit,Tolkien", text)

    async def test_main_prints_contents_and_items(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            await main(self.path)
        output = buffer.getvalue()
        self.assertIn("File contents:", output)
        self.assertIn("Title: The Hobbit, ID: 101, Author: Tolkien\n", output)
        self.assertIn("Title: Inception, ID: 201, Duration: 148 minutes\n", output)


if __name__ == "__main__":
    unittest.main()
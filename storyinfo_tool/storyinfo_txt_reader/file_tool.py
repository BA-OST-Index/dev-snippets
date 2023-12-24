import opencc
from .tool import *


class FileRewriter:
    def __init__(self, file_reader: "FileReader"):
        self.file_reader = file_reader
        self.rewrite_content = {}

    def add_rewrite_content(self, content: str, lineno: int = None):
        if lineno is None:
            lineno = self.file_reader.last_lineno

        self.rewrite_content[lineno] = content.rstrip()

    def rewrite(self):
        temp = ""
        with open(self.file_reader.filepath, "r", encoding="UTF-8") as f:
            _counter = 1
            while True:
                curr = f.readline()
                if not curr:
                    # EOF detection
                    break

                if _counter in self.rewrite_content.keys():
                    temp += self.rewrite_content[_counter] + "\n"
                else:
                    temp += curr

                _counter += 1
        with open(self.file_reader.filepath, "w", encoding="UTF-8") as f:
            f.write(temp)


class FileReader:
    def __init__(self, filepath: str, encoding: str = "utf-8"):
        self._file = open(filepath, mode="r", encoding=encoding)
        self.filepath = filepath
        self.last_read = None
        self.last_lineno = 0

        self._rewriter = FileRewriter(self)

    def __enter__(self) -> "FileReader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._file.closed:
            self._file.close()

    def readline(self, __limit: int = -1, remove_newline: bool = True) -> str:
        temp = self._file.readline(__limit)
        if not temp:
            raise EOFError

        self.last_read = temp
        if remove_newline:
            self.last_read = self.last_read.replace("\n", "").replace("\r", "")

        self.last_lineno += 1
        return self.last_read

    @property
    def last_read_autoflag(self):
        return ParserTool.punc_normalize(self.last_read)

    @property
    def last_read_is_flag(self):
        if self.last_read_autoflag in [";;", "||", "--", "//"]:
            return True
        return False

    def add_rewrite_content(self, content: str, lineno: int = None):
        self._rewriter.add_rewrite_content(content, lineno)

    def rewrite_file(self):
        self._file.close()
        self._rewriter.rewrite()

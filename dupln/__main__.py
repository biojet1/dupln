from .main import Main, flag, arg
from . import (
    add_file,
    get_linker,
    link_duplicates,
    list_uniques,
    scan_dir,
)
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from argparse import ArgumentParser
    from typing import Sequence


def filesizef(s):
    # type: (Union[int, float]) -> str
    if not s and s != 0:
        return "-"
    for x in "bkMGTPEZY":
        if s < 1000:
            break
        s /= 1024.0
    return ("%.1f" % s).rstrip("0").rstrip(".") + x


def filesizep(s: str):
    if s[0].isnumeric():
        for i, v in enumerate("bkmgtpezy"):
            if s[-1].lower().endswith(v):
                return int(s[0:-1]) * (2 ** (10 * i))
    return float(s)


class Counter(object):
    def __getattr__(self, name):
        return self.__dict__.setdefault(name, 0)

    def __contains__(self, name):
        return name in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __getitem__(self, name):
        return self.__dict__.setdefault(name, 0)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __str__(self):
        return " ".join(
            sorted(self._format_entry(k, v) for (k, v) in self.__dict__.items())
        )

    def _format_entry(self, key, value):
        return str(key) + " " + self._format_value(value, key) + ";"

    def _format_value(self, value, key):
        # type: (Any, str) -> str
        if key in ("size", "disk_size"):
            return filesizef(value)
        return str(value)


class Base(Main):
    paths: list[str] = arg("PATH", "search to", nargs="+")
    carry_on: bool = flag("carry-on", "Continue on file errors", default=None)
    total = Counter()

    def ready(self):
        if 1:
            import logging

            logging.basicConfig(
                **dict(
                    level=getattr(logging, "INFO"), format="%(levelname)s: %(message)s"
                )
            )
        # self.__annotations__
        return super().ready()

    def start(self):
        # print(self.__class__.__name__, self.__dict__)
        from logging import error, info
        from os import stat
        from stat import S_ISDIR

        db = dict()
        tot = self.total = Counter()
        carry_on = self.carry_on

        def statx(f):
            try:
                st = stat(f)
            except Exception:
                tot.file_err += 1
                if carry_on is False:
                    raise
                from sys import exc_info

                error(exc_info()[1])
                return 0, 0, 0, 0, 0

            return st.st_mode, st.st_size, st.st_ino, st.st_dev, st.st_mtime

        for x in self.paths:
            mode, size, ino, dev, mtime = statx(x)
            # print(x, S_ISDIR(mode))
            if S_ISDIR(mode):
                scan_dir(x, db, statx)
            else:
                add_file(db, x, size, ino, dev, mtime)

        try:
            self.go(db)

        finally:
            # print(len(db))
            self.total and info("Total {}".format(self.total))
        return self.total


class Stat(Base):
    def go(self, db: dict):
        link_duplicates(
            db,
            None,
            self.total,
            self.carry_on,
        )

    def init_argparse(self, argp: "ArgumentParser"):
        argp.description = r"Stats about linked files under given directory"
        return super().init_argparse(argp)


class Link(Stat):
    linker: str = flag(
        "The linker to use",
        choices=("os.link", "ln", "lns", "os.symlink"),
        default="os.link",
    )

    def go(self, db: dict):
        link_duplicates(
            db,
            get_linker(self.linker),
            self.total,
            self.carry_on,
        )

    def init_argparse(self, argp: "ArgumentParser"):
        argp.description = r"Link files under given directory"
        return super().init_argparse(argp)


class Uniques(Stat):
    def go(self, db: dict):
        list_uniques(db, self.total)

    def init_argparse(self, argp: "ArgumentParser"):
        argp.description = r"List unique files under given directory"
        return super().init_argparse(argp)


def sizerangep(s):
    f, _, t = s.partition("..")
    a, b = [filesizep(f) if f else 0, filesizep(t) if t else float("inf")]
    return lambda n: n >= a and n <= b


class Duplicates(Stat):
    size_range = flag("sizes", "size range from..to", default=None, parser=sizerangep)
    human_sizes: bool = flag("hrfs", "human readable file sizes", default=False)

    def go(self, db: dict):
        from . import list_duplicates

        kw = {}

        if self.human_sizes:
            kw["filesizef"] = filesizef

        list_duplicates(db, self.total, size_filter=self.size_range, **kw)

    def init_argparse(self, argp: "ArgumentParser"):
        argp.description = r"List duplicates files under given directory"
        return super().init_argparse(argp)


class App(Main):

    def add_arguments(self, argp: "ArgumentParser"):
        argp.prog = f"python -m {__package__}"
        argp.description = r"This command-line application scans a specified directory for duplicate files and replaces duplicates with hard links to a single copy of the file. By doing so, it conserves storage space while preserving the file structure and accessibility."
        return super().add_arguments(argp)

    def sub_args(self):
        yield Stat(), {"name": "stat"}
        yield Link(), {"name": "link"}
        yield Uniques(), {"name": "uniques"}
        yield Duplicates(), {"name": "duplicates"}


(__name__ == "__main__") and App().main()

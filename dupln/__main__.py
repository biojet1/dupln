from ocli import Base, Main, arg, flag, param
from ocli.extra import BasicLog, Counter, DryRunOpt, LogOpt


def filesizef(s):
    if not s and s != 0:
        return "-"
    for x in "bkMGTPEZY":
        if s < 1000:
            break
        s /= 1024.0
    return ("%.1f" % s).rstrip("0").rstrip(".") + x


class Counter2(Counter):
    def _format_value(self, value, key):
        # print(key, value)
        if key in ("size", "disk_size"):
            return filesizef(value)
        return str(value)


# @arg(append="paths", required="+")
# @arg("action", choices=("link", "stat", "unique_files", "debug"), required=True)
# @flag("dry_run", help="Test run")
# @flag("carry_on", help="Continue on file errors", default=None)
# @param(
#     "linker",
#     "l",
#     help="The linker to use",
#     choices=("os.link", "ln", "lns", "os.symlink"),
#     default="os.link",
# )
# class App(BasicLog, Main):
class App(LogOpt, DryRunOpt, Base):
    dry_run = False

    def options(self, opt):
        super().options(
            opt.arg(
                "action",
                choices=("link", "stat", "unique_files", "debug"),
                required=True,
            )
            .arg(append="paths", required="+")
            .flag("carry_on", help="Continue on file errors", default=None)
            .param(
                "linker",
                "l",
                help="The linker to use",
                choices=("os.link", "ln", "lns", "os.symlink"),
                default="os.link",
            )
        )

    def start(self, **kwargs):
        from logging import error, info
        from os import stat
        from stat import S_ISDIR

        from . import (Database, dump_db, get_linker, link_duplicates,
                       list_uniques, scan_dir)

        # print("start", self.__dict__)
        # print("action", self.action)
        # print("linker", self.paths)

        db = Database()
        tot = self.total = Counter2()
        carry_on = self.carry_on

        def statx(f):
            try:
                st = stat(f)
            except Exception:
                tot.file_err += 1
                if not carry_on:
                    raise
                from sys import exc_info

                error(exc_info()[1])
                return 0, 0, 0, 0, 0

            return st.st_mode, st.st_size, st.st_ino, st.st_dev, st.st_mtime

        for x in self.paths:
            mode, size, ino, dev, mtime = statx(x)
            if S_ISDIR(mode):
                scan_dir(x, db, statx)
            else:
                db.add(x, size, ino, dev, mtime)
        action = self.action

        try:
            if action == "debug":
                dump_db(db)
            elif action == "unique_files":
                list_uniques(db, self.total)
            elif action == "stat":
                link_duplicates(db, None, self.total, self.carry_on)
            elif action == "link":
                link_duplicates(
                    db,
                    get_linker(self.linker),
                    self.total,
                    self.carry_on,
                )
            else:
                raise RuntimeError(f"Unknown action {action}")
        finally:
            self.total and info("Total {}".format(self.total))
        return self.total


def main():
    return App().main()


(__name__ == "__main__") and App().main()

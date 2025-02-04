from hashlib import md5
from os.path import join, dirname, exists, samefile
from os import walk, unlink, chmod, rename, link, symlink, stat
from logging import info, error
from tempfile import mktemp
from stat import S_ISREG, S_IWUSR


def add_file(db, path, size, ino, dev, mtime):
    # type: (Dict[int, Dict[int, Dict[int, Set[str]]]], str, int, int, int, float) -> None

    dev_map = db.get(dev)
    if dev_map is None:
        dev_map = db[dev] = {}

    size_map = dev_map.get(size)
    if size_map is None:
        size_map = dev_map[size] = {}

    ino_map = size_map.get(ino)
    if ino_map is None:
        size_map[ino] = set([path])
    else:
        ino_map.add(path)

    # v = ino_map.get(path)
    # if v is None:
    #     ino_map[path] = 0


def calc_md5(src, block_size=131072):
    # type: (str, int) -> str
    m = md5()
    with open(src, "rb") as h:
        b = h.read(block_size)
        while b:
            m.update(b)
            b = h.read(block_size)
    return m.hexdigest()


def file_sort_key(x):
    # type: (str) -> float
    return stat(x).st_mtime


def link_duplicates(db, linker, tot, carry_on):
    # type: (Dict[int, Dict[int, Dict[int, Set[str]]]], Union[Callable[[str, str], None],None], Any, bool) -> None
    if len(db) > 1:
        tot.devices = len(db)
    while db:
        dev, size_map = db.popitem()
        while size_map:
            size, ino_map = size_map.popitem()
            if len(ino_map) < 2 or size < 1:
                while ino_map:
                    ino, paths = ino_map.popitem()
                    n = len(paths)
                    if n > 1:
                        tot.same_ino += 1
                    tot.files += n
                    tot.inodes += 1
                    tot.size += n * size
                    tot.disk_size += size
                continue
            else:
                tot.same_size += 1
            md5_map = (
                {} if linker else 0
            )  # type: Union[Literal[0], Dict[str, Set[str]]]

            while ino_map:
                ino, paths = ino_map.popitem()
                n = len(paths)
                if n > 1:
                    tot.same_ino += 1
                tot.files += n
                tot.inodes += 1
                if md5_map == 0:
                    tot.size += size * n
                    tot.disk_size += size
                else:
                    src = paths.pop()
                    md5 = calc_md5(src)
                    files = md5_map.get(md5)
                    if files is None:
                        md5_map[md5] = set([src])
                    else:
                        files.add(src)

            while md5_map:
                md5, files = md5_map.popitem()
                n = len(files)
                tot.size += size * n
                if n > 1:
                    tot.same_hash += 1
                    try:
                        if linker is None:
                            n = len(files)
                        else:
                            n = link_dups(linker, sorted(files, key=file_sort_key))
                    except Exception:
                        tot.link_err += 1
                        if not carry_on:
                            raise
                        from sys import exc_info

                        error(exc_info()[1])
                    else:
                        tot.linked += n
                        tot.disk_size += size
                else:  # n == 1
                    tot.unique_hash += 1
                    tot.disk_size += size


def link_dups(linker, dups):
    # type: (Callable[[str, str], None], List[str]) -> int
    src = ""
    n = 0
    while dups:
        dup = dups.pop()
        if src:
            assert dup != src
            assert exists(dup)
            tmp = mktemp(dir=dirname(dup))
            # rename dup to tmp
            rename(dup, tmp)
            assert exists(tmp)
            assert not exists(dup)
            info(" - %r - %r [%s]", dup, tmp, len(dups))
            try:  # link src to dup
                linker(src, dup)
            except OverflowError:
                # rename back on error
                if exists(tmp):
                    rename(tmp, dup)
                src = dup
                info("\t! Too many links")
            except Exception:
                # rename back on error
                info("\t! Link failed")
                if exists(tmp):
                    rename(tmp, dup)
                raise
            else:  # delete tmp
                n += 1
                assert exists(dup)
                assert samefile(src, dup)
                chmod(tmp, S_IWUSR)
                unlink(tmp)
        else:
            src = dup
            info("++ %r [%s]", src, len(dups))
    return n


def get_linker(use_linker):
    # type: (str) -> Callable[[str, str], None]
    from subprocess import call

    if use_linker == "ln":

        def fun(src, dst):
            call(["ln", src, dst])

    elif use_linker == "lns":

        def fun(src, dst):
            call(["ln", "-s", src, dst])

    elif use_linker == "os.link":

        def fun(src, dst):
            link(src, dst)

    elif use_linker == "os.symlink":

        def fun(src, dst):
            symlink(src, dst)

    else:
        raise RuntimeError(f"Unknown linker {use_linker!r}")
    return fun


def list_uniques(db, tot):
    # type: (Dict[int, Dict[int, Dict[int, Set[str]]]], Any) -> None
    tot.devices = len(db)

    while db:
        dev, size_map = db.popitem()
        tot.unique_size = len(size_map)
        while size_map:
            size, ino_map = size_map.popitem()
            while ino_map:
                ino, paths = ino_map.popitem()
                n = len(paths)
                if n > 1:
                    tot.same_ino += 1
                tot.files += n
                tot.inodes += 1
                tot.size += n * size
                tot.disk_size += size
                path = paths.pop()
                print(path)


def list_duplicates(db, tot, size_filter=None, filesizef=None):
    # type: (Dict[int, Dict[int, Dict[int, Set[str]]]], Any, Union[Callable[[int], bool],None], Union[Callable[[int], str],None]) -> None
    tot.devices = len(db)
    if filesizef is None:
        filesizef = lambda x: str(x)

    while db:
        dev, size_map = db.popitem()
        tot.unique_size = len(size_map)
        while size_map:
            size, ino_map = size_map.popitem()
            while ino_map:
                ino, paths = ino_map.popitem()
                n = len(paths)
                w = n > 1
                if w:
                    if size_filter is not None:
                        w = size_filter(size)
                    tot.same_ino += 1
                    if w:
                        print(f"+ inode:{ino} links:{n} size:{filesizef(size)}")
                        for p in paths:
                            print(f" - {p}")
                tot.files += n
                tot.inodes += 1
                tot.size += n * size
                tot.disk_size += size
                path = paths.pop()


def dump_db(db):
    # type: (Dict[int, Dict[int, Dict[int, Set[str]]]]) -> None
    from sys import stdout

    data = db.popitem()[1] if len(db) == 1 else db  # type: Any

    try:
        from yaml import safe_dump
    except ImportError:
        from json import dump, JSONEncoder

        class SetEncoder(JSONEncoder):
            def default(self, obj):
                if isinstance(obj, set):
                    return list(obj)
                return JSONEncoder.default(self, obj)

        dump(data, stdout, cls=SetEncoder, indent=4)

    else:
        return safe_dump(data, stdout, canonical=False, tags=False, indent=True)


def scan_dir(tree, db, statx):
    # type: (str, Dict[int, Dict[int, Dict[int, Set[str]]]], Callable[[str], tuple]) -> None
    info("Scanning: %r", tree)
    for root, dirs, files in walk(tree):
        for name in files:
            f = join(root, name)
            (mode, size, ino, dev, mtime) = statx(f)
            if S_ISREG(mode):
                add_file(db, f, size, ino, dev, mtime)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *

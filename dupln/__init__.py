from hashlib import md5
from os.path import join, dirname, exists, samefile
from os import walk, unlink, chmod, rename, link, symlink, stat
from logging import info, error
from tempfile import mktemp
from stat import S_ISREG, S_IWUSR


class Database(dict):
    def add(self, path, size, ino, dev, mtime):

        # dev_map = self.get((dev, size))

        dev_map = self.get(dev)
        if dev_map is None:
            dev_map = self[dev] = {}

        size_map = dev_map.get(size)
        if size_map is None:
            size_map = dev_map[size] = {}

        ino_map = size_map.get(ino)
        if ino_map is None:
            # ino_map = size_map[ino] = {}
            ino_map = size_map[ino] = set()

        ino_map.add(path)

        # v = ino_map.get(path)
        # if v is None:
        #     ino_map[path] = 0


def calc_md5(src, block_size=131072):
    m = md5()
    with open(src, "rb") as h:
        b = h.read(block_size)
        while b:
            m.update(b)
            b = h.read(block_size)
    return m.hexdigest()


def file_sort_key(x):
    return stat(x).st_mtime


def link_duplicates(db, linker, tot, carry_on):
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
            md5_map = {} if linker else 0

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
                        files = md5_map[md5] = set()
                    files.add(src)

            while md5_map:
                md5, files = md5_map.popitem()
                n = len(files)
                tot.size += size * n
                if n > 1:
                    tot.same_hash += 1
                    files = sorted(files, key=file_sort_key)
                    try:
                        n = link_dups(linker, files)
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
                    tot.uniq_hash += 1
                    tot.disk_size += size


def link_dups(linker, dups):
    src = n = 0
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
                exists(tmp) and rename(tmp, dup)
                src = dup
                info("\t! Too many links")
            except Exception:
                # rename back on error
                info("\t! Link failed")
                exists(tmp) and rename(tmp, dup)
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


def dump_db(db):
    from sys import stdout

    if len(db) == 1:
        db = db.popitem()[1]
    try:
        from yaml import dump, safe_dump
    except ImportError:
        from json import dump, JSONEncoder

        class SetEncoder(JSONEncoder):
            def default(self, obj):
                if isinstance(obj, set):
                    return list(obj)
                return JSONEncoder.default(self, obj)

        dump(db, stdout, cls=SetEncoder, indent=4)

    else:
        return safe_dump(db, stdout, canonical=False, tags=False, indent=True)


def scan_dir(tree, db, statx):
    info("Scanning: %r", tree)
    for root, dirs, files in walk(tree):
        for name in files:
            f = join(root, name)
            (mode, size, ino, dev, mtime) = statx(f)
            S_ISREG(mode) and db.add(f, size, ino, dev, mtime)

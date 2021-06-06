import hashlib
import operator
import os
import pathlib
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        values = (
        self.ctime_s,
        self.ctime_n,
        self.mtime_s,
        self.mtime_n,
        self.dev,
        self.ino,
        self.mode,
        self.uid,
        self.gid,
        self.size,
        self.sha1,
        self.flags,
        self.name.encode()
        )

        packed = struct.pack(f">10i20sh{len(self.name)}s3x", *values)
        return packed

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        format = f">10i20sh{len(data) - 62}s"
        unpacked = struct.unpack(format, data)
        unpacked_list = list(unpacked)
        unpacked_list[-1] = unpacked_list[-1][:-3].decode()
        return GitIndexEntry(*unpacked_list)



def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    index = []

    path_index = gitdir / "index"

    try :
        f = path_index.open(mode = "rb")
        data = f.read()
    except:
        return index

    count = int.from_bytes(data[8:12], "big")
    pointer = b"\x00\x00\x00"
    content = data[12:-20]
    counter = 0
    for i in range(count):
        name_len_start = counter + 62
        name_len_end = content[name_len_start:].find(pointer) + name_len_start + 3
        index.append(GitIndexEntry.unpack(content[counter:name_len_end]))
        counter = name_len_end
    return index


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    index_path = gitdir / "index"
    f = index_path.open(mode="wb")
    values = (b"DIRC", 2, len(entries))
    info = struct.pack(">4s2i", *values)
    to_hash = info
    f.write(info)
    for el in entries:
        f.write(el.pack())
        to_hash += el.pack()
    hash = hashlib.sha1(to_hash).hexdigest()
    f.write(struct.pack(f">{len(bytearray.fromhex(hash))}s", bytearray.fromhex(hash)))
    f.close()


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    entries = read_index(gitdir)
    for el in entries:
        if not details:
            print(el.name)
        else:
            print(f"{str(oct(el.mode))[2:]} {el.sha1.hex()} 0	{el.name}")


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    entries = []
    for el in paths:
        try:
            f = el.open()
            file_content = f.read()
        except:
            raise Exception("Wrong path")

        sha1 = hash_object(file_content.encode(), "blob", True)
        stat = os.stat(el)

        entries.append(
            GitIndexEntry(
                ctime_s=int(stat.st_ctime),
                ctime_n=0,
                mtime_s=int(stat.st_mtime),
                mtime_n=0,
                dev=stat.st_dev,
                ino=stat.st_ino,
                mode=stat.st_mode,
                uid=stat.st_uid,
                gid=stat.st_gid,
                size=stat.st_size,
                sha1=bytes.fromhex(sha1),
                flags=7,
                name=str(el)
            ))
    entries = sorted(entries, key=lambda x: x.name)
    if not (gitdir / "index").exists():
        write_index(gitdir, entries)
    else:
        index = read_index(gitdir)
        index += entries
        write_index(gitdir, index)

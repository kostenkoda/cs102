import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    header = f"{fmt} {len(data)}\0"
    store = header.encode() + data
    result = hashlib.sha1(store).hexdigest()
    content = zlib.compress(store)

    if write:
        workdir = pathlib.Path(".").absolute()
        gitdir = repo_find(workdir)

        if not pathlib.Path.exists(gitdir / "objects" / result[0:2]):
            (gitdir / "objects" / result[0:2]).mkdir()
        if not pathlib.Path.exists(gitdir / "objects" / result[0:2] / result[:2]):
            (gitdir / "objects" / result[0:2] / result[2:]).write_bytes(content)

    return result


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    objs = []
    if len(obj_name) > 40 or len(obj_name) < 4:
        raise Exception(f"Not a valid object name {obj_name}")

    obj_dir = gitdir / "objects" / obj_name[:2]

    for obj in obj_dir.iterdir():
        if obj_name[2:] in obj.parts[-1]:
            objs.append(
            str(obj.parts[-2]) + str(obj.parts[-1])
            )

    if not objs :
        raise Exception(f"Not a valid object name {obj_name}")

    return objs


def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    ...


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    path = gitdir / "objects" / sha[:2] / sha[2:]
    with path.open(mode = "rb") as f:
        obj_data = zlib.decompress(f.read())
        header = obj_data[: obj_data.find(b"\x00")]
        fmt = header[:header.find(b" ")]
        content = obj_data[obj_data.find(b"\x00")+1 : ]
        return fmt.decode(), content


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    result = []
    while len(data) != 0:
        mode = int(data[: data.find(b" ")].decode())
        data = data[data.find(b" ") + 1:]
        name = data[: data.find(b"\x00")].decode()
        data = data[data.find(b"\x00") + 1:]
        sha = bytes.hex(data[:20])
        data = data[20:]
        result.append((mode, name, sha))
    return result

def cat_file(obj_name: str, pretty: bool = True) -> None:
    gitdir = repo_find(pathlib.Path("."))

    for obj in resolve_object(obj_name, gitdir):
        header, content = read_object(obj, gitdir)
        if header == "tree":
            result = ""
            tree_files = read_tree(content)
            for f in tree_files:
                result += str(f[0]).zfill(6) + " "
                result += read_object(f[2], repo_find())[0] + " "
                result += f[2] + "\t"
                result += f[1] + "\n"
            print(result)
        else:
            print(content.decode())


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    result = []
    header, data = read_object(tree_sha, gitdir)
    for f in read_tree(data):
        if read_object(f[2], gitdir)[0] == "tree":
            tree = find_tree_files(f[2], gitdir)
            for blob in tree:
                name = f[1] + "/" + blob[0]
            result.append((name, blob[1]))
        else:
            result.append((f[1], f[2]))
    return result



def commit_parse(raw: bytes, start: int = 0, dct=None):
    data = zlib.decompress(raw)
    return data[data.find(b"tree") + 5: data.find(b"tree") + 45]

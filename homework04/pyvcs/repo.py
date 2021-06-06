import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    try:
        git_dir = os.environ['GIT_DIR'] if os.environ['GIT_DIR'] else ".git"
    except:
        git_dir = ".git"

    res_dir = None
    workdir=pathlib.Path(workdir)

    try:
        workdir.parents
    except:
        raise Exception("Not a git repository")

    if len(workdir.parents) == 0:
        if not pathlib.Path.exists(workdir / git_dir):
            raise Exception("Not a git repository")
        return workdir.absolute() / git_dir
    elif pathlib.Path.exists(workdir / git_dir):
        return workdir.absolute() / git_dir
    else:
        for path in workdir.parents:
            if git_dir in str(path) or pathlib.Path.exists(path / git_dir):
                res_dir = path
    if not res_dir:
        raise Exception("Not a git repository")
    if git_dir in str(res_dir):
        return res_dir
    else:
        return res_dir / git_dir


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:

#    if repo_find(workdir): raise Exception('Already a repository')

    try:
        if workdir.is_file():
            raise Exception(f"{workdir} is not a directory")
    except AttributeError:
        workdir = pathlib.Path(workdir)

    try:
        git_dir = os.environ['GIT_DIR'] if os.environ['GIT_DIR'] else ".git"
    except:
        git_dir = ".git"

    dir = workdir / git_dir
    dir.mkdir()
    (dir / "refs").mkdir()
    (dir / "refs/heads").mkdir()
    (dir / "refs/tags").mkdir()
    (dir / "objects").mkdir()
    (dir / "HEAD").write_text("ref: refs/heads/master\n")
    (dir / "config").write_text("[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n")
    (dir / "description").write_text("Unnamed pyvcs repository.\n")

    return dir

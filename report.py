import tempfile
from pathlib import Path
from utility import QuickObserver, generate_report, timestamp_now
import os
import shutil
from inspect import isgeneratorfunction

REPORT_PATH = f"reports/report_{timestamp_now()}.txt"


def write_to_report(text):
    with open(REPORT_PATH, "a", encoding="utf8") as f:
        f.write(text + "\n")
        f.write("\n")


def report(test_func):
    """a decorator, runs the decorated function until the first `yield`,
    then sets up the observer to write to a report

    The decorated function should take 1 argument, the directory Path

    - docstring -> title of test
    - `yield` -> start the observer and write to report
    - yielded value -> path to start observer
    - name of function -> useless, name it anything you want
    """
    test_title = test_func.__doc__

    if not test_title:
        raise ValueError("The function needs a docstring representing the test title!")

    if not isgeneratorfunction(test_func):
        raise ValueError("The function must have a `yield` statement!")

    with tempfile.TemporaryDirectory() as dirpath:
        dirpath = Path(dirpath)
        test_generator = test_func(dirpath)

        print(f"Running test: {test_title}")
        # run code from the beginning to the first `yield`
        observe_path = next(test_generator)
        if not observe_path:
            observe_path = dirpath

        with QuickObserver(observe_path) as ob:
            # run code until the end, catch the final StopIteration
            try:
                next(test_generator)
            except StopIteration:
                pass

        write_to_report(generate_report(test_title, ob.events, observe_path))
    
    return test_func


def xreport(test_func):
    pass


# ==============================Documentation==============================

# change `xreport` to `report` to enable this test
@xreport
def test(dir: Path):
    """example test, this doc string will be the title of the test"""
    with open(dir / "test.txt", "w") as f:
        pass
    # `yield` will start the observer then write to the report file
    # you can set the folder to be observed by passing a path to `yield`
    yield  # start observing
    os.rename(dir / "test.txt", dir / "cool_file.txt")
    os.remove(dir / "cool_file.txt")


# ==============================Basic operations==============================
write_to_report("BASIC OPERATIONS")


@report
def test(dir: Path):
    """create a folder and file, rename the file, then remove the file"""
    yield  # start observing
    (dir / "test").mkdir()
    with open(dir / "test" / "a.txt", "w") as f:
        f.write("ass")
    os.rename(dir / "test" / "a.txt", dir / "test" / "a_new.txt")
    os.remove(dir / "test" / "a_new.txt")


@report
def test(dir: Path):
    """create a file, then move it to a different folder"""
    (dir / "A").mkdir()
    (dir / "B").mkdir()
    yield  # start observing
    with open(dir / "A" / "a.txt", "w") as f:
        f.write("ass")
    os.rename(dir / "A" / "a.txt", dir / "B" / "a.txt")


# ================================Moving files================================
write_to_report("MOVING FILES")


@report
def test(dir: Path):
    """create a file, then move it to a different folder and rename at the same time"""
    (dir / "A").mkdir()
    (dir / "B").mkdir()
    yield  # start observing
    with open(dir / "A" / "a.txt", "w") as f:
        f.write("ass")
    os.rename(dir / "A" / "a.txt", dir / "B" / "a_new.txt")


@report
def test(dir: Path):
    """given a folder with 20 files, move all files to root"""
    (dir / "test").mkdir()
    file_names = [f"f{i}.txt" for i in range(0, 20)]
    for file in file_names:
        with open(dir / "test" / file, "w") as f:
            pass
    yield  # start observing
    for file in file_names:
        old_path = dir / "test" / file
        shutil.move(old_path, dir)


@report
def test(dir: Path):
    """given a folder with 10 files, move the folder to a subfolder"""
    (dir / "test").mkdir()
    (dir / "sub").mkdir()
    file_names = [f"f{i}.txt" for i in range(0, 10)]
    for file in file_names:
        with open(dir / "test" / file, "w") as f:
            pass
    yield  # start observing
    shutil.move(dir / "test", dir / "sub")


@report
def test(dir: Path):
    """given a folder with 10 files, rename the folder"""
    (dir / "test").mkdir()
    file_names = [f"f{i}.txt" for i in range(0, 10)]
    for file in file_names:
        with open(dir / "test" / file, "w") as f:
            pass
    yield  # start observing
    os.rename(dir / "test", dir / "new_folder")


@report
def test(dir: Path):
    """given a folder with 3 files and 1 subfolder with 3 files, rename the folder"""
    (dir / "base").mkdir()
    file_names_a = [f"a{i}.txt" for i in range(0, 3)]
    for file in file_names_a:
        with open(dir / "base" / file, "w") as f:
            pass
    (dir / "base" / "sub").mkdir()
    file_names_b = [f"b{i}.txt" for i in range(0, 3)]
    for file in file_names_b:
        with open(dir / "base" / "sub" / file, "w") as f:
            pass
    yield  # start observing
    os.rename(dir / "base", dir / "new_folder")


@report
def test(dir: Path):
    """create a folder with 3 files, then move all files outside observed area"""
    (dir / "observed").mkdir()
    file_names = [f"f{i}.txt" for i in range(0, 3)]
    for file in file_names:
        with open(dir / "observed" / file, "w") as f:
            pass
    yield dir / "observed"  # start observing
    for file in file_names:
        old_path = dir / "observed" / file
        shutil.move(old_path, dir)


@report
def test(dir: Path):
    """move 3 files from outside observed area to inside observed area"""
    (dir / "observed").mkdir()
    file_names = [f"f{i}.txt" for i in range(0, 3)]
    for file in file_names:
        with open(dir / file, "w") as f:
            pass
    yield dir / "observed"  # start observing
    for file in file_names:
        old_path = dir / file
        shutil.move(old_path, dir / "observed")


# =========================Deleting files=========================
write_to_report("DELETING FILES")


@report
def test(dir: Path):
    """given a folder with 5 files, delete each file"""
    (dir / "test").mkdir()
    file_names = [f"f{i}.txt" for i in range(0, 5)]
    for file in file_names:
        with open(dir / "test" / file, "w") as f:
            pass
    yield  # start observing
    for file in file_names:
        os.remove(dir / "test" / file)


@report
def test(dir: Path):
    """given a folder with 10 files, delete the folder"""
    (dir / "test").mkdir()
    file_names = [f"f{i}.txt" for i in range(0, 10)]
    for file in file_names:
        with open(dir / "test" / file, "w") as f:
            pass
    yield  # start observing
    shutil.rmtree(dir / "test")


@report
def test(dir: Path):
    """given a folder with 3 files and 1 subfolder with 3 files, delete the folder"""
    (dir / "base").mkdir()
    file_names_a = [f"a{i}.txt" for i in range(0, 3)]
    for file in file_names_a:
        with open(dir / "base" / file, "w") as f:
            pass
    (dir / "base" / "sub").mkdir()
    file_names_b = [f"b{i}.txt" for i in range(0, 3)]
    for file in file_names_b:
        with open(dir / "base" / "sub" / file, "w") as f:
            pass
    yield  # start observing
    shutil.rmtree(dir / "base")

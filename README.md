# watchdog test cases

This is a script that runs several test cases then writes all events fired by `watchdog` to a report.

Example test (in `report.py`):

```python
@report
def test(dir: Path):
    """create a folder and file, rename the file, then remove the file"""
    yield  # start observing
    (dir / "test").mkdir()
    with open(dir / "test" / "a.txt", "w") as f:
        f.write("ass")
    os.rename(dir / "test" / "a.txt", dir / "test" / "a_new.txt")
    os.remove(dir / "test" / "a_new.txt")
```

Generate a report:

```
> python report.py
Running test: create a folder and file, rename the file, then remove the file
> 
```

Generated report in `./reports/report_xxxxxxxx_xxxxxx_xxxxxx.txt`:

```
20210605_135904_294222
create a folder and file, rename the file, then remove the file
Create dir : test
Create file: test\a.txt
Modify file: test\a.txt
Modify dir : test
Move   file: test\a.txt -> test\a_new.txt
Modify dir : test
Delete file: test\a_new.txt
Modify dir : test
```

## Why?

The events fired by `watchdog` are inconsistent between operating systems, this script helps me figure out how each operating system handles each test case.

On Windows:

```
20210605_142721_019279
given a folder with 10 files, move the folder to a subfolder
Modify dir : test
Delete file: test
Create dir : sub\test
Create file: sub\test\f0.txt
Create file: sub\test\f1.txt
Create file: sub\test\f2.txt
Create file: sub\test\f3.txt
Create file: sub\test\f4.txt
Create file: sub\test\f5.txt
Create file: sub\test\f6.txt
Create file: sub\test\f7.txt
Create file: sub\test\f8.txt
Create file: sub\test\f9.txt
Modify dir : sub
```

On Ubuntu:

```
20210605_145451_761323
given a folder with 10 files, move the folder to a subfolder
Move   dir : test -> sub/test
Modify dir : .
Modify dir : sub
Move   file: test/f5.txt -> sub/test/f5.txt
Move   file: test/f4.txt -> sub/test/f4.txt
Move   file: test/f3.txt -> sub/test/f3.txt
Move   file: test/f8.txt -> sub/test/f8.txt
Move   file: test/f7.txt -> sub/test/f7.txt
Move   file: test/f6.txt -> sub/test/f6.txt
Move   file: test/f0.txt -> sub/test/f0.txt
Move   file: test/f9.txt -> sub/test/f9.txt
Move   file: test/f2.txt -> sub/test/f2.txt
Move   file: test/f1.txt -> sub/test/f1.txt
```

## Inconsistencies per operating system

### Windows

- https://github.com/gorakhargosh/watchdog/issues/775
    - Deleting a folder is detected as deleting a file
- https://github.com/gorakhargosh/watchdog/issues/393
    - Moving files is detected as _deleting then creating a file_ (test case: `given a folder with 20 files, move all files to root`)
    - Move events on windows:
        - a file is renamed in place (in the same folder)
        - renaming a folder in place (all child items also have Move event)
- When moving a folder, events are unintuitive: (test case: `given a folder with 10 files, move the folder to a subfolder`)
    1. Delete original folder (**File** deleted event is fired instead)
    2. **("Delete files in original folder" is never fired)**
    3. Create destination folder
    4. Create files in destination folder

### Unix

- Has a unique event type: `closed`
    - Can be ignored safely

import datetime as dt
from subprocess import run


def gen_msg(date: dt.datetime) -> str:
    return date.strftime("Commit: %Y.%m.%d %H:%M:%S")


def contribute(date: dt.datetime, file_name="Commit.md", msg: str = None):
    def date4git() -> str:
        return date.ctime()
    if msg is None:
        msg = gen_msg(date)
    with open(file_name, "w") as out:
        print(msg, file=out)
    run(["git", "add", "."])
    run(["git", "commit", "-m", msg, "--date", date4git()])


if __name__ == '__main__':
    contribute(dt.datetime.now())

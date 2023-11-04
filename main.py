import datetime as dt
from subprocess import run
from pathlib import Path


class GitHubDrawer:
    def __init__(self, directory: Path = Path(".")):
        self.directory = directory.absolute()
        self._today = dt.datetime.now()
        self.first = self._today - dt.timedelta(days=364)
        self.first -= dt.timedelta(days=(self.first.weekday() + 1) % 7)

    @staticmethod
    def _gen_msg(date: dt.datetime) -> str:
        return dt.datetime.now().strftime(
            f'{date.strftime("Commit time: %Y.%m.%d %H:%M:%S")}\nReal time: %Y.%m.%d %H:%M:%S')

    def get_day(self, day_from_start: int) -> dt.datetime:
        if day_from_start < 0:
            raise ValueError(f"Day from start of dashboard must be non negative, but found: {day_from_start}")
        return self.first + dt.timedelta(days=day_from_start)

    def get_day_by_week_and_day(self, week_from_start: int, day_in_week: int):
        if not (0 <= week_from_start < 53):
            raise ValueError(f"Week from start must be in range(0, 53), but found: {week_from_start}")
        if not (0 <= day_in_week < 7):
            raise ValueError(f"Day of week must be in range(0, 7), but found: {day_in_week}")

        return self.get_day(week_from_start * 7 + day_in_week)

    def contribute(self, date: dt.datetime, file_name="Commit.md", msg: str = None):
        def date4git() -> str:
            return date.ctime()

        if msg is None:
            msg = self._gen_msg(date)

        with open(self.directory / file_name, "w") as out:
            print(msg, file=out)
        run(["git", "-C", self.directory, "add", file_name])
        run(["git", "-C", self.directory, "commit", "-m", msg, "--date", date4git()])

    def draw_by_day(self, day: int, depth: int = 1):
        if not (0 <= depth < 4):
            raise ValueError()

        day = self.get_day(day)
        for i in range(depth):
            self.contribute(day, msg=f"{self._gen_msg(day)}: {i}")

    def draw_by_index(self, x: int, y: int, depth: int = 1):
        day = self.get_day_by_week_and_day(week_from_start=x, day_in_week=y)
        for i in range(depth):
            self.contribute(day, msg=f"{self._gen_msg(day)}: {i}")

    def push(self, force: bool = False):
        run(["git", "-C", self.directory, "push", "--force" if force else ""])

    def update(self, days: int = 1):
        """
        git filter-branch --env-filter '
        COMMIT_DATE=$(git log $GIT_COMMIT -n1 --format=%aD);
        NEW_DATE=$(date -d "$COMMIT_DATE+1 day" -R);
        GIT_COMMITTER_DATE="$NEW_DATE"
        export GIT_COMMITTER_DATE
        GIT_AUTHOR_DATE="$NEW_DATE"
        export GIT_AUTHOR_DATE
        ' SHA..HEAD
        """


if __name__ == '__main__':
    d = Path(r"D:\Projects\PycharmProjects\res")
    g = GitHubDrawer(d)
    # g.draw_by_day(10, 3)
    with open("test.txt", encoding="utf-8") as inp:
        data = inp.read().splitlines()

    start_week = 4
    for x in range(len(data[0])):
        for y in range(len(data)):
            g.draw_by_index(x + start_week, y, int(data[y][x]))
    g.push()

    # print(g.first)
    # print(g.first.weekday())
    # print(dt.date(2023, 11, 5).weekday())

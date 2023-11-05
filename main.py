import datetime as dt
from subprocess import run, PIPE
from pathlib import Path


def parse_draw(file_p: Path):
    with open(file_p, encoding="utf-8") as inp:
        data = inp.read().splitlines()
    data = [tuple(map(int, tuple(line))) for line in data]
    return data


class Drawer:
    def __init__(self, directory: Path = Path("."), branch="surface",
                 remote_name="origin", remote_url=None):
        self.directory = directory.absolute()
        self.surface_start_day = dt.datetime.now() - dt.timedelta(days=364)
        self.surface_start_day -= dt.timedelta(days=(self.surface_start_day.weekday() + 1) % 7)
        self.branch = branch
        self.r_name = remote_name
        self.r_url = remote_url

        self.prepare_git()
        self.prepare_branch()

    def git(self, cmds: list[str], pipe_out: bool = True, *args, **kwargs):
        """Run git command in right directory."""
        if pipe_out:
            return run(["git", "-C", self.directory] + cmds,
                       stdout=PIPE, stderr=PIPE, text=True, *args, **kwargs)
        return run(["git", "-C", self.directory] + cmds, *args, **kwargs)

    def prepare_git(self):
        """
        Check that there is git in the directory.
        Аnd creates a repository if it does not exist.
        """

        def check_exits_git():
            """Check that git is installed."""
            try:
                self.git([])
            except OSError:
                raise Exception("You need a git")

        def check_exist_repository():
            """Check that git repository exists in directory."""
            r = self.git(["status"])
            # TODO: Add log
            if r.returncode:
                return False
            return True

        def create_rep():
            """Create a git repository in directory"""
            self.git(["init", "-b", self.branch], pipe_out=False)

        check_exits_git()
        if check_exist_repository():
            return
        create_rep()

    def prepare_branch(self):
        """Check that the branch exists and creates it if not."""

        def branch_list():
            """Get list of repository branches."""
            return self.git(["branch"]).stdout.splitlines()

        def parse_current(branches):
            """Get name of current branch."""
            for b in branches:
                if b[0] == "*":
                    return b.lstrip("*").lstrip()

        def check_exist(branches):
            """Check that the required branch exists."""
            for b in branches:
                if b.lstrip == self.branch:
                    return True
            return False

        def switch2current():
            """Switch repository to the required branch."""
            return self.git(["checkout", self.branch])

        def create_and_switch():
            """Create the required branch and switch on it."""
            return self.git(["checkout", "-b", self.branch])

        b_list = branch_list()
        if parse_current(b_list) == self.branch:
            return

        if check_exist(b_list):
            switch2current()
        else:
            create_and_switch()

    def prepare_remote(self):
        """Check that the remote repository is connected and try to connect it."""
        def check_exist_remote():
            r = self.git(["remote", "show", self.r_name])
            # TODO: Add log
            if r.returncode:
                return False
            return True

        def connect_remote():
            self.git(["remote", "add", self.r_name, f'"{self.r_url}"'])

        if check_exist_remote():
            return
        if self.r_url is None:
            raise Exception("The url of remote repository is not set.")
        connect_remote()

    def get_day_by_week_and_day(self, week_from_start: int, day: int):
        return self.surface_start_day + dt.timedelta(weeks=week_from_start, days=day)

    def commit(self, date: dt.datetime, msg: str, file_name="README.md"):
        def date4git() -> str:
            return date.ctime()

        with open(self.directory / file_name, "w") as out:
            print(msg, file=out)

        self.git(["add", file_name])
        self.git(["commit", "-m", date.strftime("%Y.%m.%d %H:%M:%S"), "--date", date4git()], pipe_out=False)

    def fill_cell(self, x: int, y: int, depth: int = 1):
        """Fill cell of activity bar."""
        def gen_msg(date: dt.datetime, d: int) -> str:
            return (
                f"This is an empty repository created specifically for drawing by GitHub activity.\n"
                f"{dt.datetime.now().strftime('Current commit time: %Y.%m.%d %H:%M:%S')}\n"
                f"{date.strftime('Recorded commit time: %Y.%m.%d %H:%M:%S')}({d})\n"
                f"Look at: github.com/baderik/ActivityDrawer")

        day = self.get_day_by_week_and_day(week_from_start=x, day=y)
        for i in range(depth):
            self.commit(day, msg=gen_msg(day, i))

    def push(self, force: bool = True):
        """Prepare remote and push new surface."""
        self.prepare_remote()
        self.git(["push", self.r_name, self.branch, "--force" if force else ""])

    def move_branch_commits(self, days: int = 7):
        """Move all commits forward a specified number of days."""
        delta_seconds = 86400 * days
        update_command = (
                "   date_str = commit.author_date.decode('utf-8')\n"
                "   seconds, timezone = date_str.split()\n"
                "   new_date = f'{int(seconds) + " + str(delta_seconds) + "} {timezone}'\n"
                "   commit.author_date = new_date.encode('utf-8')")
        self.git(["filter-repo", "--commit-callback", update_command, "--force"])

    def move_surface(self, weeks: int = 1):
        """Move the old surface for a week."""
        self.move_branch_commits(weeks * 7)

    def reset_current_branch(self) -> None:
        """Reset all commits of branch."""
        # TODO: Check that it won't take down other branches... I'm not sure)
        first_commit = self.git(["rev-list", "--max-parents=0", "HEAD"]).stdout.strip()
        self.git(["reset", "--hard", first_commit], pipe_out=False)

    def reset_surface(self):
        """Reset surface by reset all commits branch."""
        self.reset_current_branch()

    def draw(self, mtx, shift: int = 0):
        """
        Draw a given matrix of the number of commits with a shift of the start week.
        """
        if not mtx:
            return
        for x in range(len(mtx[0])):
            for y in range(len(mtx)):
                self.fill_cell(x + shift, y, int(mtx[y][x]))


if __name__ == '__main__':
    d = Path(r"..\surface")
    g = Drawer(d, remote_name=r"https://github.com/Baderik/ActivitySurface")
    g.reset_surface()
    f = Path(r"templates/dnk.txt")
    m = parse_draw(f)
    g.draw(m)
    g.push()

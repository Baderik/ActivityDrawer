*Pet project*
# ActivityDrawer
A script drawing activity on the GitHub activity bar.

## Requirements

----
* git
* git-filter-repo
* python 3.9

## Using

---
```parse_draw(file_path)``` - get matrix from template file.

```Drawer``` - Base class for interacting with the GitHub activity bar.
\
### Init arguments:
* directory: path to directory with repository. The folder must exist
* branch: name of branch. Base: surface
* remote_name: shortname of remote repository. Base: origin
* remote_url: url for remote repository. Needed if the remote repository is not connected.

### draw(matrix, shift):
Draw spawn commits on the right dates. Matrix - set of count commits at day. Shift - indent from the left border.

### move_surface(week):
Shift the entire drawing surface for a given number of weeks (1 week = 1 column).

### reset_surface():
> GitHub does not update activity, even if you change the commit history. It's useless right now.

Cleans the surface by clean the commit history of branch.

### push():
Just push local repository to remote repository. 
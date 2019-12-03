# Scanner

This is a simple script that will update a git repo and scan it with the source clear tool.

By default it loads the file `data/repos.json`.
`data/sample-repos.json` is a sample of how this file is created.
Each repo should follow the following structure.

```json
{
    "name": "Sample Project Name",
    "ssh": "git@github.com:Sample/sample-project-name.git",
    "location": "/ptah/on/local/disc/to/sample-project-name",
    "projects": [
        ".",
        "subpackage/path"
        ]
}
```

All the reports are saved in the folder `out`.
If this folder is not present, then create the folder in the root.
Reports are over writen each time the scan is ran.

While looking at the reports its import to look for errors.
If there are any errors, note that there is no way to run the script on a single repo.

To run the project.

```bash
python main.py
```

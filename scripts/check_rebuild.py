#!/usr/bin/env python
# Fails if the web site needs a rebuild.

import os

built_in = "page.html", "macros.py", "scripts/macros.py", "scripts/poole.py"
project_mtime = max([os.stat(fn).st_mtime for fn in built_in])

for folder, folders, filenames in os.walk("input"):
    for filename in filenames:
        if filename.endswith(".md"):
            src = os.path.join(folder, filename)
            dst = "output/" + src[6:-2] + "html"

            if not os.path.exists(dst):
                exit(1)

            dst_mtime = os.stat(dst).st_mtime
            if dst_mtime < project_mtime:
                exit(1)

            src_mtime = os.stat(src).st_mtime
            if dst_mtime < src_mtime:
                exit(1)

exit(0)

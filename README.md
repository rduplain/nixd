nixd: Relatively self-contained configuration management.
---------------------------------------------------------

Can configuration be as simple as `make boot` for your stack? Experimental.

Usage:

1. Put enclosed nixd directory in a project. Update version control excludes.
2. Update project Makefile with the `boot` target below. Note literal tab.
3. Add/symlink nixd configuration scripts to nixd/etc/. See nixd/lib/.
4. Type `make boot`. Build make targets which use `boot` as dependency.
5. Profit.

In your Makefile:

    boot:
    	nixd/bin/nixd boot

Copyright 2012 Ron DuPlain. BSD licensed.

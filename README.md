nixd: Relatively self-contained configuration management.
---------------------------------------------------------

Can configuration be as simple as `make boot` for your stack? Experimental.


### Usage

1. Put enclosed `nixd` directory in a project. Update version control excludes.
2. Update project Makefile with the `boot` target below. Note literal tab.
3. Add/symlink nixd configuration scripts to `nixd/etc/`. See `nixd/lib/`.
4. Type `make boot`. Build make targets which use `boot` as dependency.
5. Profit.

In your Makefile:

    boot:
    	nixd/bin/nixd boot


### Goals

For Make-appropriate self-contained application stacks on Unix-derived systems:

1. Provide a simple framework to build and configure *across* dependencies.
2. Prefix dependency installation to chroot-able project-specific directory.
3. Support simple local mirroring to cache all dependencies.
4. Ease/encourage use of dependency forks, by mirroring the forked version.
5. Use stdio & the command-line to allow use of any style of executable.
6. Defer to rebuilding instead of uninstalling, given local mirroring.
7. Defer to OS for system-level dependencies. Support checking installation.


Copyright 2012 Ron DuPlain. BSD licensed.

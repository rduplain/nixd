nixd: Relatively self-contained configuration management.
---------------------------------------------------------

Can configuration be as simple as `make boot` for your stack? Experimental.


### Usage

1. Put enclosed `nixd` directory in a project. Update version control excludes.
2. Update project Makefile with the `boot` target below. Note literal tab.
3. Add/symlink nixd package scripts to `nixd/bin/`. See `nixd/lib/`.
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


### Motivation

I want the exact usage and goals listed above, and this project will illustrate
a specific use case. More generally, I want to configure *environments* not
*systems*. Given a shell account (or platform-as-a-service hook), compose
simple commands to check that everything is ready and install anything
missing. This is particularly motivated by application stacks which have
source-installed binaries and incorporate multiple programming environments,
for example, those using mongrel2 and redis with a process manager.

This is not to replace existing tools, just compose them in a simple manner.

Let's not forget about Make. I would like `make boot` so that I can define
higher level targets which depend on boot, and if the `boot` target is checking
that everything is installed *before* running, then we can prevent embarrassing
subsystem mismatch errors at runtime which are not immediately obvious given
the inevitable opaque error message.

Then, we get `make run` which works across development environments & staging.


Copyright 2012 Ron DuPlain. BSD licensed.

nixd: self-contained configuration management.
----------------------------------------------

Can configuration be as simple as `make boot` for your stack? Experimental.

It's pronounced "nixed", like "mixed" but with an 'n'.


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


### Mirroring / In-House Package Server

Once your package scripts are ready to share across development/staging
environments, you can set new environments to pull *all* declared resources
from an in-house package server or the local filesystem to download once & run
often. This provides efficiency for distribution and reliability that all
dependencies are online for download, and allows for curated review of
downloads before spreading across the organization's network. In one nixd
setup:

    ./nixd/bin/nixd download

Then make ./nixd/src available as static files on an in-house httpd. From other
nixd deployments with the same set of package scripts:

    NIXD_MIRROR=https://resources.example.org/nixd/src/ ./bin/nixd boot

You could also use the filesystem, or any other URL that curl understands:

    NIXD_MIRROR=file:///var/lib/nixd/src/ ./bin/nixd boot


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


### Design Principles

1. Clearly log activity. Fail loudly and immediately.
2. Plan for primitive operations to be run repeatedly. Finish quickly.
3. Do not write a DSL for file management. We already have one: shell.
4. Set up `nixd boot` to run without dependencies on all target systems.
5. It's safe to use GNU bash and bashisms everywhere.
6. Readability counts.
7. Avoid gymnastics. Readability counts most in packaging scripts.
8. Use dynamic binding carefully. Explicitly export within a "nixd" namespace.


Copyright (c) 2012, Ron DuPlain. BSD licensed.

nixd: self-contained configuration management.
----------------------------------------------

nixd is a simple configuration management framework to build development and
runtime environments for software projects targeting Unix/Unix-like systems.

It's pronounced "nixed", like "mixed" but with an 'n'.

Status: alpha.


### Introduction

Your favorite developer tools and packages include instructions on where to
download the latest release and how to configure and install for your
environment. You already have a means to commission new machines with your
configuration (salt, chef, puppet, ...) and install underlying system packages
(.deb, .rpm, ports, pacman, ...), but these do not provide a straightforward
solution to *boot your environment* -- to translate the instructions of your
preferred developer packages into a reliable, automated task.

You could include a boot task in your build system (make, maven, rake, ...),
but the effort is non-trivial to keep the boot task efficient, resilient to
downtime of your community hosting services, reliable across target
environments, readable, and maintainable. It's nixd role to make this effort
trivial. Trivial and grokkable. Write automation hooks your team can easily
understand.

In configuration management terms, nixd is a local execution
environment. Provide a shell, call `nixd boot`, then run your project.


### Example

Download and install Redis if `redis-server` is not already installed:

    #!/bin/bash

    ARCHIVE=redis-2.6.7.tar.gz
    UNPACKED=redis-2.6.7

    check() {
        file $NIXD_PREFIX/bin/redis-server
    }

    resources() {
        echo http://redis.googlecode.com/files/$ARCHIVE
    }

    install() {
        tar -xzf $ARCHIVE
        cd $UNPACKED
        PREFIX=$NIXD_PREFIX make install test
    }

    nixd_run "$@"


### Usage

1. Put enclosed `nixd` directory in a project. Update version control excludes.
2. Update project Makefile with the `boot` target below. Note literal tab.
3. Add/symlink nixd package scripts to `nixd/bin/`. See `nixd/lib/`.
4. Type `make boot`. Build make targets which use `boot` as dependency.
5. Profit.

In your Makefile:

    boot:
    	nixd/bin/nixd boot


### Goals for Use

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

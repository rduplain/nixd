nixd: self-contained configuration management.
----------------------------------------------

nixd is a simple configuration management framework to build development and
runtime environments for software projects targeting Unix/Unix-like systems.

It's pronounced "nixed", like "mixed" but with an 'n'.

Status: alpha, ready for testing across popular Unix/Unix-like systems.


### Introduction

Your favorite developer tools and packages include instructions on where to
download the latest release and how to configure and install for your
environment. You already have a means to commission new machines with your
configuration (salt, chef, puppet, ...) and install underlying system packages
(.deb, .rpm, ports, pacman, ...), but these do not provide a straightforward
solution to *install your environment* -- to translate the instructions of your
preferred developer packages into reliable, automated tasks which are run at
the right times.

You could include an install task in your build system (make, maven, rake,
...), but the effort is non-trivial to keep the install task efficient,
resilient to downtime of your community hosting services, reliable across
target environments, readable, and maintainable. It's nixd role to make this
effort trivial. Trivial and grokkable. Write automation hooks your team can
easily understand.

In configuration management terms, nixd is a local execution
environment. Provide a shell, call `nixd install`, then run your project.


### Example

Download and install Redis if `redis-server` is not already installed:

    #!/bin/bash

    ARCHIVE=redis-2.6.7.tar.gz
    UNPACKED=redis-2.6.7

    check() {
        ls $NIXD_PREFIX/bin/redis-server
    }

    resources() {
        echo http://redis.googlecode.com/files/$ARCHIVE
    }

    install() {
        tar -xzf $ARCHIVE
        cd $UNPACKED
        PREFIX=$NIXD_PREFIX make install
    }

    nixd_run "$@"

Put this simple script in your repo-tracked nixd configuration, and you can
ensure redis is installed correctly whenever you checkout and run your project.


### Usage

Create a `nixd` directory within your project, and download the `nixd` program:

    cd path/to/your/project
    mkdir -p nixd/bin/
    curl -o nixd/bin/nixd https://raw.github.com/rduplain/nixd/master/bin/nixd
    cat nixd/bin/nixd # Read and make sure you are comfortable executing it.
    chmod a+x nixd/bin/nixd

Repeat these instructions verbatim to update `nixd` to the latest version.

If you already have a working `nixd` executable, you can instead use the
`selfinstall` command to create the `nixd/bin` directory and copy the
executable:

    cd path/to/your/project
    nixd selfinstall .

Next, add scripts to `nixd/sbin/` to provide packages for your environment. See
[script examples here](https://github.com/rduplain/nixd/tree/master/lib). The
pattern is:

* *check* - exit with status 0 if already installed, non-zero otherwise.
* *resources* - print required downloads to stdout, one on each line.
* *install* - unpack those downloads and install them to `$NIXD_PREFIX`.

Unix conventions apply. Each script in `nixd/sbin` must be executable. The
script is invoked `nixd/sbin/scriptname subcommand` where subcommand is
*check*, *resources*, or *install*. An exit status of 0 indicates success, and
a non-zero exit status indicates an error (which should stop nixd
execution). Commands *check* and *install* do not have any stdio requirements,
but *resources* must declare line-by-line its required URLs to stdout.

It's important to declare all direct downloads through the *resources*
subcommand. This lets nixd manage the downloads and support caching & in-house
mirroring. The *install* subcommand is run with a working directory where the
resources are downloaded. To provide meaningful filenames, you can list a local
filename on the same line as the URL, separated by a space. Use a format of one
of:

    http://example.com/package.tar.gz
    http://example.com/1.0/package.tar.gz package-1.0.tar.gz

In the first case, the remote name of package.tar.gz is used locally. In the
second case, the remote file is downloaded locally to a file named
package-1.0.tar.gz.

Note that nixd's convention is to load a filesytem hierarchy based on where the
program itself is loaded on disk. This design supports self-contained
installations relative to where the nixd program is installed, and is why you
should create a dedicated `nixd/bin` directory. The hierarchy is as follows,
with the indicated environment variables pointing to the full filepath:

* nixd/usr/ - prefix to use in installation (NIXD_PREFIX)
* nixd/bin/ - directory containing `nixd` program & utilities (NIXD_BIN)
* nixd/sbin/ - directory containing `nixd` package scripts (NIXD_SBIN)
* nixd/etc/ - directory for any configuration files (NIXD_ETC)
* nixd/src/ - base directory for downloads (NIXD_SRC)
* nixd/src/NAME - download directory for package script with NAME (NIXD_RES)

The `etc/` directory can hold any static files you need. Simply reference these
files in your package scripts.

The reason to download the nixd script instead of a system-wide install, is to
provide for a self-sufficient install process. Build yourself a distribution
which can boot an environment on all of your target systems without worrying
about dependencies. If you have detailed OS-level dependencies, write nixd
scripts which verify them (in *check*) and print out instructions (in
*install*) when they are not met (returning a non-zero exit status on *install*
to halt execution).

**Do** provide locally compiled packages like redis or mongrel2. **Do not**
compile complex packages provided by your operating system -- use the tools
provided by the OS to inspect and install packages (which you can do in a nixd
script).

If your project has *ordered dependencies*, you can specify the names of the
scripts in the correct order as arguments to nixd. In this example, nixd will
install package1 then package2, then install all packages on the second call to
nixd:

    nixd install package1 package2
    nixd install

If you use a Makefile, you can create an install target like this one (note
literal tab), and create targets which use `install` as a dependency:

    install:
    	nixd/bin/nixd install

Clean would then be (carefully) as follows. If you want to keep resource
downloads and builds around, do not remove `nixd/src/`.

    clean:
    	rm -fr nixd/usr/ nixd/opt/ nixd/var/ nixd/src/

Then you'd have have your project run with the pattern of:

    run: install
    	nixd/usr/bin/your-process-manager arguments

Typically you will use a process manager (foreman, supervisord, circus, procer,
...) to contain all of your project's processes, the initial install process
for which is why nixd exists.

Note that 'nixd' and 'all' are reserved and cannot be used as package names.


### Goals for Use

1. Provide a simple framework to build and configure *across* dependencies.
2. Prefix dependency installation to chroot-able project-specific directory.
3. Support simple local mirroring to cache all dependencies.
4. Provide a simple means to specify dependency order.
5. Ease use of dependency forks, by mirroring the forked version.
6. Use stdio & the command-line to allow use of any style of executable.
7. Defer to rebuilding instead of uninstalling, given local mirroring.
8. Defer to OS for system-level dependencies. Support checking installation.


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

    NIXD_MIRROR=https://resources.example.org/nixd/src/ ./bin/nixd install

You could also use the filesystem, or any other URL that curl understands:

    NIXD_MIRROR=file:///var/lib/nixd/src/ ./bin/nixd install


### Design Principles

1. Clearly log activity. Fail loudly and immediately. Make it obvious.
2. Plan for primitive operations to be run repeatedly. Finish quickly.
3. Do not write a DSL for file management. We already have one: shell.
4. Have `nixd install` run without unusual dependencies on all target systems.
5. Embrace Unix. Use exit status and stdio effectively.
6. It's safe to use GNU bash and bashisms everywhere.
7. Readability counts.
8. Avoid gymnastics. Readability counts most in packaging scripts.
9. Use dynamic binding carefully. Explicitly export within a "nixd" namespace.

Design principle #1 has two competing sub-objectives: fail loudly and fail
immediately. If a nixd process fails at some intermediate step in its
implementation, which will likely happen when testing support for new
underlying operating systems, "fail immediately" could lead to a quiet
error. In this case, run `bash -x nixd/bin/nixd install` (or other subcommand)
to see the trace in bash to determine where it failed.


Copyright (c) 2012-2013, Ron DuPlain. BSD licensed.

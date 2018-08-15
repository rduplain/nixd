# nixd builds unix daemons and environments

nixd builds u**nix** **d**aemons and environments by providing a download/build
workflow which embeds into any build system.


### Project Status

nixd is stable and in regular use by contemporary projects. Source commits are
infrequent because the project is simple and stable, depending only a version
of GNU bash which is both widely available and was released more than a decade
ago.


### Motivation and Design

_Make_ (i.e. GNU make) as a build tool is relevant to any project -- not just
C/C++ -- when viewed as a _dependency-driven shell environment_. It can run
commands just like shell. After all, Makefile recipes are line-by-line
command-line invocations. When these lines get complicated, the Makefile gets
complicated. The nixd project started specifically to provide a full shell
framework to invoke advanced tasks with a single line inside of a Makefile.

Build recipes in nixd are only run if a recipe's *check* fails. Where a
Makefile relies on files and timestamps, a nixd recipe defines a check
command. This check can rely on files and timestamps, too, but can be
*anything*. The implementation of the check is its own (often _tiny_) program;
nixd is checking whether that program runs successfully.

If the check fails, the program gets called again with predefined subcommands
to download *resources*, configure, and *install* a given requirement, as
appropriate. This approach is particularly useful when combining multiple
programming languages or embedding a service into a project. Simple programs
become recipes to fetch, unpack, and configure the necessary tools. These
recipes are executable specs which are repeatable without having to vendor
external code into the project repository.

This does not only apply to Makefiles. All build systems (in Unix) have a
concept of executing a shell-like command to run a step. Shell is a great tool
to define step-by-step commands (i.e. a _script_) to configure and install a
requirement. nixd provides a simple framework to download and install
accordingly, and to only run when needed.

Above all, nixd does this without adding any additional dependencies.


### Use Cases

1. Install developer tools and services in place. This is suitable for small
   tools, and is particularly useful for a monorepo or or any project which
   benefits from local integration testing (at which point a
   [Procfile][Introducing Procfile] is relevant [see also:
   [poorman][poorman]]).
2. Configure Unix systems with a minimal configuration management system.
   Recipes in nixd can naturally handle system configuration workflows as
   there's no limitation to which files a shell program can access (using sudo
   as needed).
3. Provide a simple entry point for a nontrivial step inside of some other
   configuration workflow. For example, call out as a line within a remote
   script run over SSH or as a step in a Dockerfile.

These use cases are mutually exclusive. **Specifically, do not modify system
files while installing developer tools and services in-place.**

[Introducing Procfile]: http://blog.daviddollar.org/2011/05/06/introducing-foreman.html
[poorman]: https://github.com/rduplain/poorman


### This Is Not

1. A build tool which replaces other build tools. Each programming community
   has its own set of tooling, and this project does not replace any of
   them. Instead, it bootstraps tools needed for the build.
2. An abstraction over operating systems. Instead, it embraces the underlying
   operating system and provides a framework for managing small programs.
3. Limited to shell. Instead, it uses conventional subcommands, interacts over
   stdio, and inspects exit status codes.


### Example

Download and install [Redis](https://redis.io/).

```bash
#!/usr/bin/env bash

UNPACKED=redis-4.0.11
ARCHIVE=$UNPACKED.tar.gz
SHA256=fc53e73ae7586bcdacb4b63875d1ff04f68c5474c1ddeda78f00e5ae2eed1bbb

check() {
    # Installs to this location, which local to the project.
    # See if the file exists.
    ls $NIXD_PREFIX/bin/redis-server
}

resources() {
    local url=http://download.redis.io/releases/$ARCHIVE
    echo $url $ARCHIVE sha256 $SHA256
}

install() {
    tar -xf $ARCHIVE
    cd $UNPACKED
    PREFIX=$NIXD_PREFIX make install
}

nixd_run "$@"
```


### Usage

Create a hidden .nixd directory within a project, and download `nixd`:

```bash
cd path/to/project
mkdir -p .nixd/bin/
cd .nixd/bin
curl -o nixd https://raw.githubusercontent.com/rduplain/nixd/master/bin/nixd
cat nixd # Read and make sure it is okay to execute.
chmod a+x nixd
```

Repeat these instructions to update `nixd` to the latest version. It is okay to
check the `nixd` program into other project repositories, if appropriate.
Otherwise, a bootstrap script is available to avoid doing this. Check
`bin/nixd-bootstrap` into a project repository, and download nixd with:

```bash
sha256=1bc4594ab25f71673fc958997852243e5e137863f90de16d8a21a42a999e7b6a
.nixd/bin/nixd-bootstrap .nixd/bin/nixd v0.4 sha256 $sha256
```

The goal of nixd is to provide a self-sufficient install process, by which a
developer can check out a project and run a single command to bootstrap the
application environment. Accordingly, the nixd executable is relative to the
project and not a system-wide install.

Next, add scripts to .nixd/sbin/ to install and configure dependencies.
Recipes are invoked with conventional subcommands:

* *check* - exit with status 0 if already installed, non-zero otherwise.
* *resources* - print required downloads to stdout, one per line (optional).
* *pretest* - test for install dependencies, system headers (optional).
* *install* - unpack those downloads and install them to `$NIXD_PREFIX`.

Unix conventions apply. Each script in .nixd/sbin must be executable. The
script is invoked `.nixd/sbin/scriptname subcommand` where subcommand is
*check*, *resources*, *pretest*, or *install*. An exit status of 0 indicates
success, and a non-zero exit status indicates an error (which will stop nixd
execution). Commands *check* and *install* do not have any stdio requirements,
but *resources* must declare line-by-line its required URLs to stdout.

It's important to declare all direct downloads through the *resources*
subcommand. This lets nixd manage the downloads and support caching & in-house
mirroring. The *pretest* and *install* subcommands are run with a working
directory where the resources are downloaded. To provide meaningful filenames,
a resource can list a local filename on the same line as the URL, separated by
a space. Use a format of one of:

    http://example.com/package.tar.gz
    http://example.com/1.0/package.tar.gz package-1.0.tar.gz
    http://example.com/package.tar.gz package.tar.gz sha256 c0ffee0123456789

In the first case, the remote name of package.tar.gz is used locally. In the
second case, the remote file is downloaded locally to a file named
package-1.0.tar.gz.

Note that nixd's convention is to use a filesytem hierarchy based on where the
program itself is located on disk. This design supports self-contained
installations relative to where the nixd program is installed, and is why nixd
expects a dedicated .nixd/bin directory by convention. The hierarchy is as
follows, with the indicated environment variables pointing to the full absolute
filepath:

* .nixd/usr/ - prefix to use in installation (NIXD_PREFIX)
* .nixd/bin/ - directory containing `nixd` program & utilities (NIXD_BIN)
* .nixd/sbin/ - directory containing `nixd` recipe scripts (NIXD_SBIN)
* .nixd/etc/ - directory for any configuration files (NIXD_ETC)
* .nixd/src/ - base directory for downloads (NIXD_SRC)
* .nixd/src/NAME - download directory for recipe script with NAME (NIXD_RES)

The etc/ directory can hold any static files as needed. Simply reference
these files in recipe scripts.

**Do** provide locally compiled packages such as redis. **Do not** compile
complex packages provided by the operating system -- use the tools provided by
the OS to inspect for the necessary tools (in *check*) and print out
installation instructions (in *install*).

If a project has *ordered dependencies*, specify the names of the recipes in
the correct order as arguments to nixd. In this example, nixd will install
package1 then package2, then install all packages on the second call to nixd:

```Makefile
nixd install package1 package2
nixd install all
```

A Makefile pulls this together:

```Makefile
install:
	nixd install package1 package2
	nixd install all
```

A make target to start the project then depends on the install target:

```Makefile
run: install
	path/to/project-specific start with-arguments
```

A clean target would then remove the output directories, which are best
included by .gitignore, too. To keep resource downloads and builds around,
retain .nixd/src/.

```Makefile
clean:
	rm -fr .nixd/usr/ .nixd/opt/ .nixd/var/ .nixd/src/
```

Note that 'nixd' and 'all' are reserved and cannot be used as recipe names.


### Mirroring

Once nixd recipes are ready to share across development/staging environments,
nixd can pull *all* declared resources from an in-house mirror or the local
filesystem. This allows for a cache for repeatability and offline usage,
assuming that no recipe sideloads data beyond what is declared in the
*resources* step. In one nixd setup:

    .nixd/bin/nixd download

Then make .nixd/src available as static files on an in-house httpd. From other
nixd deployments with the same set of package scripts:

    NIXD_MIRROR=https://resources.example.org/nixd/src/ .nixd/bin/nixd install

The local fileystem is supported instead of an in-house httpd, as well as any
other URL that curl understands:

    NIXD_MIRROR=file:///var/lib/nixd/src/ .nixd/bin/nixd install

Note that mirroring is "all or nothing" such that nixd doesn't check upstream
if a resource is missing in the mirror.


### Exit Codes

    0: Success
    1: General error
    2: Incorrect invocation
    3: Bad configuration of nixd
    127: Command not implemented (for use in optional recipe commands)


### Debugging

nixd has a design principle to fail loudly and immediately. These objectives
sometimes compete. During development of nixd itself, if a nixd process fails
at some intermediate step, "fail immediately" could lead to a quiet error. In
this case, run `bash -x bin/nixd install` (or other subcommand) to see the
trace in bash to determine where it failed.

---

Copyright (c) 2012-2018, Ron DuPlain. BSD licensed.

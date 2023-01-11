# pltfrm
⛅ Handy wrapper tool around docker &amp; docker-compose to manage your applications

## 🧠 Motivation

Running my own little Docker-powered cloud composed of a few services at home, I often find myself going from service
directory to service directory in `docker-compose up` the different stacks when doing any sort of operations that
involve multiple services at once. Scripting and using `invoke` only gets so far before becoming cruft itself, tooling
emerges.

`pltfrm` tries to solve that problem by wrapping the most common use cases of that kind of grunt work to get stacks
going using a simple(r) command set.

## ⚠ Disclaimer

This tool is currently primarily meant for my own use cases and isn't quite ready for outside contributions. I do
welcome suggestions and critique though.

Use at your own risks. Until a v1.0.0 release is made, anything can potentially be a breaking change, and breaking
changes will be signalled in the releases' changelog.

## 📦 Installation

Artifacts will eventually get released automagically on tag creation, but until then, you can either fetch the assets from the Github releases or build it yourself by via `cargo build`.

## 🔨 Usage

`pltfrm --help` is the best documentation on usage:

```
Handy wrapper tool around docker & docker-compose to manage your applications

Usage: pltfrm [OPTIONS] <ACTION> [TARGETS]...

Arguments:
  <ACTION>      Action to take
  [TARGETS]...  Collection of projects to apply the action on

Options:
      --config-path <CONFIG_PATH>  Defines the path to the pltftm configuration file
  -b, --build                      If truthy, containers will be rebuilt before being started
  -a, --all                        If truthy, all containers defined in the config are processed, targets are ignored
  -v, --verbose                    If truthy, subcommand output is printed out after execution. Note that failure is always noisy
  -h, --help                       Print help information
  -V, --version                    Print version information
```

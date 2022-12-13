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

Until this is released anywhere, you can install it directly from source via `pip install
git+https://github.com/mcataford/pltfrm.git#egg=pltfrm`.

## 🔨 Usage

`pltfrm --help` is the best documentation on usage:

```
usage: pltfrm [-h] [-v] [-a] [--cwd CWD] {start,stop} ...

Makes handling multi-docker-projects environments a bit easier.

positional arguments:
  {start,stop}   Action to take.
    start        Starts target projects.
    stop         Stops running target projects.

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Extra output, including forwarded output from docker.
  -a, --all      Applies the command to all known projects.
  --cwd CWD      Directory used as root when looking for configuration files.
```

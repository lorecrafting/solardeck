# ARCHIVAL_BUILD.md — Making This Repo Buildable in 2056

Written 2026-10-20 11:40 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

## The question: why "impossible to reconstruct in 2046"?

Not dramatic language — a specific, already-happened failure mode.

Right now `src/daemons/` builds against a toolchain that exists only in **registries and mirrors that
are not in this repo**. To rebuild `eink-refreshd` in 2046 you need, simultaneously and in compatible
versions:

1. A compiler for the host ABI of the target. `gcc` 13.x is on Debian's servers today. Whether Debian
   still serves `bookworm` aports in 2046 is unknown; the average lifespan of a distro archive point
   release is ~5–8 years before it becomes a museum mirror or disappears.
2. The exact **dependency versions** in `apt`/`pip`/`cargo`/`npm`. Registries get deleted. npm has
   removed packages; Rust crates have been yanked; apt sources get pruned. A `Cargo.lock` names a
   version that no server is obligated to keep.
3. The **linux headers** for kernel 6.6 at the patch level the drivers were tested against. Kernel
   tarballs on kernel.org survive; distribution patches and build configs do not.
4. A **build script** that still runs. `Makefile` targets break on new make versions; `./configure`
   probes hosts that no longer respond; `pip install` reaches for the network.
5. **Credentials and submodules.** Anything fetched with a token, or a git submodule pointing at a URL
   that may be gone, is a hole that only appears on a fresh clone.

Any **one** of those five missing makes the rebuild fail, and there is no partial credit: a daemon you
can't compile is a daemon you can't fix. The evidence that this is real isn't hypothetical — it is the
ordinary experience of trying to build a 1995 package today, where the *only* thing that works is the
copy somebody happened to snapshot, with its compiler, in one tarball.

The second-order failure is worse than the first: the hardware also ages out. In 2046 there is no
guaranteed source for a CM4, an IT8951, or a Kaleido panel. So the 30-year plan cannot be "rebuild the
same thing". It has to be **"re-implement against a frozen spec, on whatever silicon exists then"** —
which means the *specification and the build recipe* are the durable artifact, and the binaries are
disposable.

## What the archival container is

One self-contained directory, checked into git, that reconstructs the build **with no network access**:

```
tools/archival/
├── README.md                  # the exact commands, and what each one proves
├── toolchain.lock             # compiler, headers, and dep versions by content digest (sha256)
├── sources/                   # vendored source tarballs, not URLs
│   ├── gcc-13.2.0.tar.xz
│   └── linux-headers-6.6.tar.xz
├── deps/                      # vendored crates/pip wheels/npm tarballs
├── rootfs.tar.gz              # the bootable-ish build root, ~300 MB
└── build.sh                   # runs inside the container; refuses network
```

The rules that make it worth something:

1. **Digest-pinned, not tag-pinned.** `debian:bookworm@sha256:…`, never `debian:bookworm`. A tag is a
   mutable pointer; a digest cannot be retargeted.
2. **No network at build time.** `build.sh` runs with `--network=none`. If it works offline, registries
   dying is irrelevant. If it needs the network, it is not archival — it is a convenience.
3. **Vendor the sources and the dependencies.** A lock file records intent; a vendored tarball records
   bytes. Only bytes survive.
4. **Reproducible bit-for-bit.** Same inputs ⇒ same sha256 of every output. That is what turns "it
   built for me" into "it is the same binary as the one on the device".
5. **Tested on a schedule.** An archive nobody runs is decaying silently. Add a CI job that runs the
   offline build **yearly**, not just on PRs — the failure you are guarding against is the death of a
   URL nobody is watching.

## Why this is cheap now and expensive later

Cost today: one afternoon and ~300 MB in git (or an LFS/release asset). Every input is still reachable.
Cost in 2046: reconstructing a 2026 build environment from memory and partial mirrors, with no way to
prove the result matches what shipped. The information-theoretic version of the problem: the entropy
needed to rebuild is *available for free right now* and *irrecoverable later*. That asymmetry is the
whole argument.

## The honest size of it

This is **not** the highest-value work in the repo — three audits in, the blockers are still the BOM
arithmetic and the absence of a certification path. It is the highest *leverage-per-hour* work,
because it is small, bounded, and closes a door that never reopens. It is on the list at P1 for that
reason, not as a distraction from P0.

## Key custody (same cliff, different shape)

A 30-year device cannot depend on a signing key someone remembers. Two offline shares: one printed in
the physical vault, one with the owner; both listed in this document by location and holding date, never
by value. An unpowered device with an unrecoverable key is a brick that boots.

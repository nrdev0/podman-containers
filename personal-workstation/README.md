# Personal workstation

Podman development container for x86-64 and ARM64. Starts as `dev` in `/workspace`
with Fish. Requires Podman; on macOS, start the Podman machine first.

## Installed tools and versions

| Component | Version policy |
| --- | --- |
| Debian | `trixie-slim` (moving tag, not digest-pinned) |
| Neovim | Pinned: **0.12.5** |
| Tree-sitter CLI | Pinned: **0.27.0** |
| OpenCode | Pinned: **1.18.31** (npm) |
| herdr terminal multiplexer | Pinned: **0.9.1**, with architecture-specific SHA-256 checksums |
| Git, OpenSSH client, ripgrep, Fish, Node.js/npm | Debian trixie packages; not version-pinned |
| Python 3, pip, venv, GCC/G++/make (`build-essential`) | Debian trixie packages; not version-pinned |
| curl, CA certificates, ncurses-term, unzip, xz-utils | Debian trixie packages; not version-pinned |
| Neovim plugins (NvChad, Kanagawa, etc.) | Locked in `dotfiles/nvim/.config/nvim/lazy-lock.json`; installed on first Neovim launch |
| Mason language tools | Not version-locked; installed during Neovim setup |

Unpinned Debian packages use the versions available in trixie at build time,
not necessarily the latest upstream releases. Update pinned tools through the
`Containerfile` version arguments; herdr also requires updated checksums.

## Build and run

From `personal-workstation/`:

```sh
podman build -t localhost/personal-workstation .
./run

# Refresh the base image and Debian packages, keeping pinned tool versions
podman build --pull=always --no-cache -t localhost/personal-workstation .
```

`./run` accepts a command, e.g. `./run nvim`. Exit the main shell to stop and
remove the container; run `./run` again to start a new one. After rebuilding,
start a new container to use the updated image.

## Persistent files and dotfiles

| Named volume | Mount | Contents |
| --- | --- | --- |
| `personal-workstation-home` | `/home/dev` | Configuration, plugins, history, authentication |
| `personal-workstation-projects` | `/workspace` | Repositories and build outputs |

Volumes are created automatically and survive container removal and rebuilds.
Files elsewhere are temporary. No host folders are mounted or ports published.

- Startup copies missing Fish, Neovim, and herdr files from the image into `~/.config`, preserving existing files and symlinks.
- Edit `dotfiles/` and rebuild to distribute defaults. Existing homes keep their copies; back up and move aside files you want replaced, then run `setup-dotfiles` inside the new container.
- Machine-specific Fish settings go in `~/.config/fish/local.fish`.
- herdr defaults in `~/.config/herdr/config.toml`: Nord theme, `Ctrl+s` prefix, pane history disabled.

## First-time setup

Inside the container, set your Git identity:

```sh
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

For SSH Git access, create a key with `ssh-keygen -t ed25519`, add the public key
to your Git host, and test GitHub access with `ssh -T git@github.com`.
Keys persist in `~/.ssh`.

Select a [Nerd Font](https://www.nerdfonts.com/) in your **host terminal**.
Launch `nvim`, wait for plugin installation, then run:

```vim
:Lazy restore
:MasonInstallAll
:TSInstallAll
```

Use `:Lazy restore` after updating the home's plugin lockfile; use `:checkhealth`
to diagnose Neovim issues.

## Everyday commands

```sh
git clone git@github.com:OWNER/REPOSITORY.git
cd REPOSITORY
nvim .
opencode
herdr
```

- OpenCode: use `/connect` in its TUI to configure authentication.
- herdr: `Ctrl+s`, then `q` detaches with the bundled config; `herdr` reattaches while the container is running. Exiting the container's main shell ends its sessions.

# Personal workstation

Two files: a Containerfile and this README. Requires Podman; on macOS, its
Podman machine must be running.

Installs Neovim, Tree-sitter CLI, OpenCode, Git, ripgrep, tmux, fish, Node.js/npm,
Python 3 with pip and venv support, unzip, xz-utils,
and `build-essential` (including GCC, G++, and make), plus supporting packages
for installation and terminal use. No custom dotfiles or Git credential settings.

Neovim comes from the latest stable upstream Linux release, including its runtime
files and bundled dependencies, rather than Debian's older package. Both x86-64
and ARM64 images are supported. It is installed under `/usr/local`; other system
packages come from Debian trixie. Tree-sitter CLI also comes from the latest stable
upstream Linux release. Editor plugins and language servers are installed
separately as needed.

## Build

From this directory:

```sh
podman build -t localhost/personal-workstation .
```

To refresh Neovim, Tree-sitter CLI, OpenCode, and Debian packages, bypass the cached build layers
and pull the current base image:

```sh
podman build --pull=always --no-cache -t localhost/personal-workstation .
```

Start a new container from the rebuilt image to use the updated tools.

## Run

```sh
podman run --rm -it \
  --name personal-workstation \
  --userns keep-id:uid=1000,gid=1000 \
  --env TERM=xterm-256color \
  --volume personal-workstation-home:/home/dev \
  --volume personal-workstation-projects:/workspace \
  localhost/personal-workstation
```

Podman creates the named volumes on first use:

| Volume | Location | Contents |
| --- | --- | --- |
| `personal-workstation-home` | `/home/dev` | Tool configuration, plugins, history, and authentication state |
| `personal-workstation-projects` | `/workspace` | Cloned repositories and build outputs |

The home volume stores the whole container home so Neovim, OpenCode, and other
tools can use their normal paths. Both directories are prepared for the `dev`
user in the image. No host folders are mounted and no ports are published.

## Git setup (once per home volume)

Run these commands inside the container as `dev`. Replace the example name and
email with your own; for GitHub, you can use the noreply email shown in your
account's email settings.

```fish
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

Git saves these settings in `/home/dev/.gitconfig`, so they survive container
replacement and image rebuilds. For a different identity in a particular project,
run `git config user.email "you@work.example"` from that repository (without
`--global`).

### SSH authentication

Create a dedicated workstation key in the persistent home:

```fish
mkdir -p ~/.ssh
chmod 700 ~/.ssh
if not test -e ~/.ssh/id_ed25519; and not test -e ~/.ssh/id_ed25519.pub
    ssh-keygen -t ed25519 -C "personal-workstation" -f ~/.ssh/id_ed25519
end
cat ~/.ssh/id_ed25519.pub
```

Choose a passphrase when prompted. The guard preserves an existing key pair when
you repeat these instructions. Add the displayed **public key** to your Git
hosting account; for GitHub, use **Settings > SSH and GPG keys > New SSH key**
and select an authentication key.

Test the connection:

```fish
ssh -T git@github.com
```

On the first connection, compare the host-key fingerprint with
[GitHub's published fingerprints](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)
before accepting it. A successful GitHub test says you authenticated successfully
but shell access is not provided; its exit status is normally 1.

The private key and known-host records stay in `/home/dev/.ssh`. SSH asks for the
key passphrase when needed; no SSH agent is configured.

For a repository already cloned using HTTPS, switch its remote from inside the
repository:

```fish
git remote set-url origin git@github.com:OWNER/REPOSITORY.git
```

## NvChad setup (once per home volume)

The image includes the tools required by the
[NvChad quickstart](https://nvchad.com/docs/quickstart/install): Neovim, Git,
Tree-sitter CLI, GCC, make, and ripgrep. Curl and archive utilities support plugin
and Mason downloads; Node.js/npm and Python pip/venv support common language tools.
Additional Mason packages may require their own language runtimes.

### Terminal font (on the host)

Install a [Nerd Font](https://www.nerdfonts.com/) on your host operating system,
then select it in the terminal application's font/profile settings. For example,
NvChad recommends **JetBrainsMono Nerd Font** rather than **JetBrainsMono Nerd
Font Mono**, whose icons can appear smaller.

The host terminal renders all text and icons, including when using Podman or tmux.
The container does not need font packages or access to host font directories.

### Install inside the container

If you already have a Neovim configuration, back it up and move it out of
`~/.config/nvim` before cloning. When switching from another distribution, also
back up and move aside `~/.local/share/nvim`, `~/.local/state/nvim`, and
`~/.cache/nvim` to start with clean plugin data.

```fish
git clone https://github.com/NvChad/starter ~/.config/nvim
nvim
```

Wait for lazy.nvim to finish installing plugins, then run these inside Neovim:

```vim
:MasonInstallAll
:TSInstallAll
```

After a successful fresh clone, remove the starter repository's Git metadata as
directed by NvChad (only if it is still the unmodified starter checkout):

```fish
rm -rf ~/.config/nvim/.git
```

Configuration, plugins, parsers, and Mason tools are stored in the home volume and
survive image rebuilds. Use `:Lazy sync` to update plugins. For troubleshooting,
run `:checkhealth` and `:checkhealth mason` in Neovim, and `tree-sitter --version`
in the shell.

## Work

The container starts in fish, which is also the `dev` user's default shell.
Customize it in `~/.config/fish/config.fish`; its configuration and history persist
in the home volume.

Inside the container:

```sh
git clone git@github.com:OWNER/REPOSITORY.git
cd REPOSITORY
nvim .
opencode
```

OpenCode authentication can be configured using `/connect` inside its TUI.

Add your own configuration under `/home/dev`, such as `~/.config/nvim/init.lua`.
A new home volume starts without custom dotfiles.

Exit the shell to remove the container; the named volumes remain. Run the same
`podman run` command again to resume using your files and settings. Rebuild the
image when changing installed tools. Files outside the two volumes are temporary.

## If you used the previous bundle

Save work, then stop and remove its container before using the new run command:

```sh
podman stop personal-workstation
podman rm personal-workstation
```

The volume names are unchanged, so existing projects and home files are reused.
Previously installed dotfiles or user Git settings remain in that home; this
simplification does not delete your existing configuration.

## Validation

Podman was unavailable where these files were authored, so the image build and
runtime have not been tested here. The build includes Neovim version and headless
startup checks and a Tree-sitter CLI version check. The first build downloads
Debian packages, Neovim and Tree-sitter CLI from GitHub, and OpenCode from npm;
versions are not pinned yet. NvChad's interactive plugin installation must be
completed inside the running workstation.

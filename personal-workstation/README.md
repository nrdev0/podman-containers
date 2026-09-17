# Personal workstation

A Containerfile, version-controlled dotfiles, and setup/run scripts. Requires
Podman; on macOS, its Podman machine must be running.

Installs Neovim, Tree-sitter CLI, OpenCode, Git, ripgrep, herdr, fish, Node.js/npm,
Python 3 with pip and venv support, unzip, xz-utils,
and `build-essential` (including GCC, G++, and make), plus supporting packages
for installation and terminal use. On startup, the image automatically copies
missing Fish and Neovim configuration files into `/home/dev/.config`.

Both x86-64 and ARM64 images are supported. Neovim (including its runtime),
Tree-sitter CLI, and [herdr](https://herdr.dev) use upstream Linux releases under
`/usr/local`. OpenCode comes from npm; system packages come from Debian trixie.

The Containerfile pins Neovim 0.12.5, Tree-sitter CLI 0.27.0, OpenCode 1.18.31,
and herdr 0.9.1 through build arguments. Herdr's architecture-specific SHA-256
checksums are pinned too. Update the version arguments (and herdr checksums) in
the Containerfile to record an upgrade. The Debian base tag and apt repositories
still move, and Mason tools are not version-locked, so builds are not bit-for-bit
reproducible. Neovim plugins are locked in `dotfiles/nvim/.config/nvim/lazy-lock.json`.

## Build

From this directory:

```sh
podman build -t localhost/personal-workstation .
```

To refresh Debian packages and the base image while reinstalling the pinned tools:

```sh
podman build --pull=always --no-cache -t localhost/personal-workstation .
```

Start a new container from the rebuilt image to use the updated tools.

## Run

```sh
./run
```

`run` records the container name, user mapping, terminal environment, and volumes.
It works from any working directory and accepts an optional container command,
for example `./run fish`. Podman creates the named volumes on first use:

| Volume | Location | Contents |
| --- | --- | --- |
| `personal-workstation-home` | `/home/dev` | Tool configuration, plugins, history, and authentication state |
| `personal-workstation-projects` | `/workspace` | Cloned repositories and build outputs |

The home volume stores the whole container home so Neovim, OpenCode, and other
tools can use their normal paths. Both directories are prepared for the `dev`
user in the image. No host folders are mounted and no ports are published.

## Dotfiles setup

The dotfiles were imported from `/home/dev`. The repository contains:

| Directory | Default configuration |
| --- | --- |
| `fish` | `~/.config/fish/config.fish`, with an optional `local.fish` include |
| `nvim` | NvChad Lua configuration, Kanagawa theme, and the plugin lockfile |

There was no herdr configuration to import. Its defaults apply. Fish's generated
universal variables, histories, caches, installed plugins, `node_modules`, and
authentication data are not part of the dotfiles source.

On a new computer, clone this repository, build the image, and run `./run` as
shown above. The build includes a snapshot of `dotfiles/` at
`/usr/local/share/workstation/dotfiles`. The container entrypoint runs
`setup-dotfiles` as `dev` before starting Fish (or your supplied command).

Setup copies regular files into `/home/dev/.config`. A fresh home automatically
gets the complete default configuration. On later starts, only missing files are
copied; existing files and symlinks are preserved. Setup also avoids following
symlinked directories. You can rerun `setup-dotfiles` manually at any time.

The repository remains the source of truth for distributed defaults. The files
in the home volume are independent copies: editing them does not change the
repository. Neither a checkout inside the container nor host bind mounts are
required.

### Migrating an existing home volume

Existing configuration is preserved automatically. To replace it with the image's
defaults, move the old configuration into a backup directory, then rerun setup.
This also replaces links created by the earlier Stow setup with regular copies.
This Fish example resets Neovim and the main Fish configuration file:

```fish
set backup (mktemp -d "$HOME/dotfiles-backup.XXXXXX")
mkdir -p "$backup/fish"
if test -e ~/.config/nvim; or test -L ~/.config/nvim
    mv ~/.config/nvim "$backup/"
end
if test -e ~/.config/fish/config.fish; or test -L ~/.config/fish/config.fish
    mv ~/.config/fish/config.fish "$backup/fish/"
end
setup-dotfiles
```

If the old `~/.config` or `~/.config/fish` directory itself is a symlink, move that
link aside and create a regular directory before applying defaults. Back up any
edits in an old symlink's source before removing its checkout or container.
Restart Fish after replacing its configuration.

Review backups for settings you want to keep. Existing Neovim plugin data remains;
use `:Lazy restore` to align it with the tracked lockfile. If switching from another
Neovim distribution, also back up and move aside its data, state, and cache directories.

### Editing and updating

Manually edit `personal-workstation/dotfiles/` in this repository, commit your
changes, and rebuild the image to distribute updated defaults. New home volumes
receive those defaults automatically. Existing home volumes keep their current
files; use the reset procedure above to adopt the rebuilt image's defaults.
Files removed from the repository are not automatically deleted from existing homes.

Local edits under `~/.config` and plugin lockfile updates from `:Lazy update`
remain in the home volume. If you want to distribute those changes, manually
copy the desired content into this repository and commit it. Reload or restart
the affected application after changing its active configuration.

## Git setup (once per home volume)

Set your Git identity inside the container:

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

The host terminal renders all text and icons, including when using Podman or herdr.
The container does not need font packages or access to host font directories.

### Install inside the container

The dotfiles are copied automatically at container startup. Launch Neovim:

```fish
nvim
```

Wait for lazy.nvim to finish installing plugins. Its first bootstrap checks out
the commit in the tracked lockfile. Restore plugins to that lock, then install tools:

```vim
:Lazy restore
:MasonInstallAll
:TSInstallAll
```

Plugins, parsers, and Mason tools are stored in the home volume and survive image
rebuilds, along with the copied configuration.
Use `:Lazy restore` after updating the home's lockfile from the repository. For troubleshooting,
run `:checkhealth` and `:checkhealth mason` in Neovim, and `tree-sitter --version`
in the shell.

## Work

The container starts in fish, which is also the `dev` user's default shell.
Customize the tracked Fish config in the repository, or add machine-specific
settings in `~/.config/fish/local.fish`. Local settings and history persist in the
home volume.

Run `herdr` inside the container to open the terminal multiplexer, then run your
shell commands and tools in its panes. Press `Ctrl+b`, then `q` to detach; run
`herdr` again to reattach while the container is running. Exiting the container's
main shell stops the container and its running processes, including herdr sessions.
See the [herdr quick start](https://herdr.dev/docs/quick-start/) for pane controls.

Inside the container:

```sh
git clone git@github.com:OWNER/REPOSITORY.git
cd REPOSITORY
nvim .
opencode
```

OpenCode authentication can be configured using `/connect` inside its TUI.

Add shared defaults to the repository's `dotfiles/` directory. Keep local overrides
and authentication in `/home/dev`.

Exit the shell to remove the container; the named volumes remain. Run the same
`./run` command again to resume using your files and settings. Rebuild the
image when changing installed tools. Files outside the two volumes are temporary.

## If you used the previous bundle

Save work, then stop and remove its container before using the new run command:

```sh
podman stop personal-workstation
podman rm personal-workstation
```

The volume names are unchanged, so existing projects and home files are reused.
Previously installed dotfiles or user Git settings remain in that home; follow
the migration instructions above before applying the managed dotfiles.

## Validation

Run the copy/setup tests from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s personal-workstation/tests
```

These cover fresh-home regular-file copies, repeated setup, local changes,
new defaults, and existing symlinks. The pinned Linux release URLs were checked
for both supported architectures.

Podman was unavailable where these files were authored, so the image build and
runtime have not been tested here. The build includes Neovim version and headless
startup checks and Tree-sitter CLI and herdr version checks. The first build downloads
Debian packages, Neovim, Tree-sitter CLI and herdr from GitHub, and OpenCode from npm.
NvChad's interactive plugin installation must be completed inside the workstation.

if status is-interactive
    # Commands to run in interactive sessions can go here
end

# Machine-specific settings belong in the persistent home volume.
if test -f ~/.config/fish/local.fish
    source ~/.config/fish/local.fish
end

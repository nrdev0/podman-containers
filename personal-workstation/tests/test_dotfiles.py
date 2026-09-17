import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


WORKSTATION = Path(__file__).resolve().parents[1]


class DotfilesSetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=WORKSTATION)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.source = self.root / "dotfiles"
        shutil.copytree(WORKSTATION / "dotfiles", self.source)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "WORKSTATION_DOTFILES_DIR": str(self.source),
            "PATH": str(WORKSTATION) + os.pathsep + os.environ["PATH"],
        }

    def setup(self):
        return subprocess.run(
            [str(WORKSTATION / "setup-dotfiles")], env=self.env,
            check=True, capture_output=True, text=True,
        )

    def test_fresh_home_copies_regular_files(self):
        self.setup()
        for package in ("fish", "nvim"):
            for source in (self.source / package).rglob("*"):
                target = self.home / source.relative_to(self.source / package)
                self.assertFalse(target.is_symlink())
                if source.is_file():
                    self.assertEqual(source.read_bytes(), target.read_bytes())

    def test_repeat_setup_preserves_edits_and_adds_missing_defaults(self):
        self.setup()
        config = self.home / ".config/fish/config.fish"
        config.write_text("# local edit\n")
        new_default = self.source / "fish/.config/fish/new.fish"
        new_default.write_text("# new default\n")
        self.setup()
        self.assertEqual(config.read_text(), "# local edit\n")
        self.assertNotEqual(
            (self.source / "fish/.config/fish/config.fish").read_text(),
            config.read_text(),
        )
        self.assertEqual(
            (self.home / ".config/fish/new.fish").read_text(), "# new default\n"
        )

    def test_existing_directory_symlink_is_not_followed(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.home / ".config").symlink_to(outside, target_is_directory=True)
        self.setup()
        self.assertEqual(list(outside.iterdir()), [])

    def test_dangling_file_symlink_is_preserved(self):
        fish = self.home / ".config/fish"
        fish.mkdir(parents=True)
        target = self.root / "missing"
        link = fish / "config.fish"
        link.symlink_to(target)
        self.setup()
        self.assertTrue(link.is_symlink())
        self.assertFalse(target.exists())

    def test_entrypoint_sets_up_before_running_command_and_returns_status(self):
        result = subprocess.run(
            ["sh", str(WORKSTATION / "entrypoint"), "sh", "-c",
             'test -f "$HOME/.config/nvim/init.lua" || exit 99; exit 17'],
            env=self.env, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 17, result.stderr)


if __name__ == "__main__":
    unittest.main()

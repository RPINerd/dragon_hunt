import os
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class StartupTest(unittest.TestCase):
    def test_module_selection_reaches_new_game_screen(self) -> None:
        env = os.environ.copy()
        env["SDL_VIDEODRIVER"] = "dummy"
        env["SDL_AUDIODRIVER"] = "dummy"
        script = textwrap.dedent(
            """
            import pygame
            import config

            event_reads = 0

            def get_events(*args, **kwargs):
                global event_reads
                event_reads += 1
                key = pygame.K_RETURN if event_reads == 1 else pygame.K_ESCAPE
                return [pygame.event.Event(pygame.KEYDOWN, key=key)]

            pygame.event.get = get_events
            import rpg

            rpg.main()

            assert config.MODULES == ["DarkAges", "DragonHunt"], config.MODULES
            assert pygame.display.get_init()
            assert pygame.display.get_surface() is not None
            assert event_reads == 2, event_reads
            print("STARTUP_SMOKE_OK")
            """
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=PROJECT_ROOT / "src",
            env=env,
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("STARTUP_SMOKE_OK", result.stdout)

    def test_module_discovery_filters_incomplete_folders(self) -> None:
        env = os.environ.copy()
        env["SDL_VIDEODRIVER"] = "dummy"
        env["SDL_AUDIODRIVER"] = "dummy"
        script = textwrap.dedent(
            """
            from pathlib import Path
            from tempfile import TemporaryDirectory

            import pygame
            pygame.init()
            import modules

            with TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                valid = root / "ValidModule"
                (valid / "data" / "maps").mkdir(parents=True)
                (valid / "data" / "variables.txt").touch()
                (valid / "data" / "maps" / "start.txt").touch()

                placeholder = root / " "
                (placeholder / "images").mkdir(parents=True)

                missing_map = root / "MissingMap"
                (missing_map / "data" / "maps").mkdir(parents=True)
                (missing_map / "data" / "variables.txt").touch()

                assert modules.discover_installed_modules(root) == ["ValidModule"]
            """
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=PROJECT_ROOT / "src",
            env=env,
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_module_picker_window_close_exits_cleanly(self) -> None:
        env = os.environ.copy()
        env["SDL_VIDEODRIVER"] = "dummy"
        env["SDL_AUDIODRIVER"] = "dummy"
        script = textwrap.dedent(
            """
            import pygame
            pygame.init()
            import config
            config.MODULES = ["DarkAges", "DragonHunt"]

            event_reads = 0
            def get_events(*args, **kwargs):
                global event_reads
                event_reads += 1
                return [pygame.event.Event(pygame.QUIT)]

            pygame.event.get = get_events
            import rpg
            rpg.main()

            assert event_reads == 1, event_reads
            assert not pygame.get_init()
            print("PICKER_QUIT_OK")
            """
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=PROJECT_ROOT / "src",
            env=env,
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PICKER_QUIT_OK", result.stdout)

    def test_module_picker_escape_cancels(self) -> None:
        env = os.environ.copy()
        env["SDL_VIDEODRIVER"] = "dummy"
        env["SDL_AUDIODRIVER"] = "dummy"
        script = textwrap.dedent(
            """
            import pygame
            pygame.init()
            import config
            config.MODULES = ["DarkAges", "DragonHunt"]

            pygame.event.get = lambda *args, **kwargs: [
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
            ]
            import modules
            assert modules.select() is None
            assert pygame.get_init()
            print("PICKER_CANCEL_OK")
            """
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=PROJECT_ROOT / "src",
            env=env,
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PICKER_CANCEL_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()

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

            config.MODULES = ["DarkAges", "DragonHunt"]
            event_reads = 0

            def get_events(*args, **kwargs):
                global event_reads
                event_reads += 1
                key = pygame.K_RETURN if event_reads == 1 else pygame.K_ESCAPE
                return [pygame.event.Event(pygame.KEYDOWN, key=key)]

            pygame.event.get = get_events
            import rpg

            rpg.main()

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


if __name__ == "__main__":
    unittest.main()

# TODO

Larger scale tasks beyond the scope of just a todo flag in the code

- [ ] Remove all instances where `global var` is used
- [x] Make a central logging system with consistent formatting.
- [ ] Create a button class structure that allows buttons to do their own collision detection and actions
- [ ] Conform with RUFF coding standards
- [ ] Have full google style docstrings for all functions
- [ ] Central `key_handler()` if possible
- [ ] Depricate the use of multiple `mouse_handle_move()` functions; should be able to use pygame mouse pos passed to button class
- [ ] All script() functions use same input, could be a factory or class or construct or something?
- [ ] Item should be a class with inherited children for each item type (equipment, healing, etc)
- [ ] A battle (encounter?) should be a single class to share variables and status of combat

## Next Step Game Plan

1) [x] Fix and test startup first. Initialize Pygame before importing modules that create the display, use the project environment in `Play`, and add a smoke test that reaches the new-game screen.

2) [x] Make save/load a single coherent feature. Saves now use a validated, versioned JSON format shared by the loader and save preview. Round-trip tests cover player stats, equipment, inventory, skills, map position, dropped items, turn timing, and script variables.

3) [x] Make module selection reflect installed modules. Discover module folders with the required data, filter incomplete folders and placeholders, validate module loads, and exit cleanly when the picker is cancelled or closed.

4) Correct combat input handling. In battle.py, event.key == config.BINDINGS["action"] or config.BINDINGS["attack"] is true for every key because the attack binding is a nonzero integer. Compare event.key against both bindings, then test navigation, action, attack, and unrelated keys separately.

5) Build a broader regression baseline. Startup and persistence smoke tests are in place. Add focused gameplay tests for combat and map interactions, and address migration diagnostics before broad cleanup like the structural items in this TODO.

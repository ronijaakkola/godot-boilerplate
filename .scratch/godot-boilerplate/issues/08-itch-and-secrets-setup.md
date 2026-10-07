# Set up the itch.io project and butler API key in GitHub secrets

Type: task
Status: resolved
Blocked by: 03

## Question

HITL. Create the itch.io project page (HTML5, embed settings incl. SharedArrayBuffer per research), generate a butler API key, create the GitHub repo, and store the key as a GitHub Actions secret. Record the itch.io `user/game` target, channel name and secret name here.

Note (from ticket 01): use the no-threads build; leave itch's experimental SharedArrayBuffer option **off**. itch's CDN gzips `.wasm`/`.pck` itself.

Note (from ticket 03): names to use — secret `BUTLER_API_KEY`, repository variable `ITCH_TARGET=<user>/<game>`, channel `html5`. After the first butler push, manually tick "This file will be played in the browser" on the `html5` upload — itch never auto-tags it.

## Comments

- From the core-systems design ticket: the game has no fullscreen setting, so it relies on itch's embed **fullscreen button**. Turn it on in the itch project's embed options.

## Answer

Done. Facts later tickets depend on:

- **GitHub repo**: https://github.com/ronijaakkola/godot-boilerplate. It's **public**, so branch protection and required checks work on the free plan. `main` is pushed and `origin` is set.
- **itch.io target**: `nashtanir/game-off-2026` (https://nashtanir.itch.io/game-off-2026). It's an HTML project in **Draft**, so the URL returns 404 to anyone else until it's published. Embed settings follow this ticket: fullscreen button on, SharedArrayBuffer off. These are set in the itch UI and couldn't be checked from the CLI.
- **Channel**: `html5`.
- **Secret**: `BUTLER_API_KEY`, an itch API key generated in the user's settings and stored as a repo Actions secret.
- **Variable**: `ITCH_TARGET=nashtanir/game-off-2026`, a repo Actions variable.
- **Still to do after the first butler push** (Build the CI pipeline): tick "This file will be played in the browser" on the `html5` upload.

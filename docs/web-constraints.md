# Web constraints

The game ships as a web build on itch.io, and **web wins** over visual ambition: when an effect doesn't work on the web, drop it. Read this before touching shaders, the environment, lighting, loading or audio.

Facts are for Godot 4.7.2. Sources and detail are in the [renderer research](../.scratch/godot-boilerplate/research/01-web-renderer-and-export-limits.md).

## Renderer

The web runs only the **Compatibility** renderer (WebGL 2). There is no WebGPU, so no Forward+ or Mobile on the web. The whole project uses Compatibility, so the editor shows what players get.

**Works on the web, and builds the soft look:**

- Tonemap **AgX** (or Filmic). Adjustments and a 3D LUT for a pastel grade.
- Ambient light from the sky or a constant pastel colour.
- **SSAO**: only Radius and Intensity apply.
- **Glow**, simplified: Screen blend only, with a low threshold for soft bloom on emissives.
- **Depth and height fog**, with Sun Scatter.
- One shadowed DirectionalLight with soft PCF filtering, plus a few unshadowed omni lights. The limit is 8 omni and 8 spot lights per mesh.
- **Toon** diffuse in StandardMaterial3D, or a custom `light()` ramp in a spatial shader.
- Outlines with **Grow** on an unshaded next-pass material (Cull Front), or the Outline stencil mode. Both need smooth-shaded, connected meshes.
- **MSAA 3D**, the only edge antialiasing on the web.
- Baked **LightmapGI** renders, but baking needs a Vulkan, D3D12 or Metal GPU: bake in the editor on a dev machine. CI can't bake.

**Missing on the web:** volumetric fog and FogVolume (fake local mist with quad sprites), SSR, SSIL, SDFGI, VoxelGI, DOF, auto exposure, decals, debanding, FXAA/SMAA/TAA, textured area lights, the normal-roughness buffer (so no normal-based screen-space edges), compute shaders and CompositorEffects.

**Costs to plan for:**

- Each post effect (glow, SSAO, adjustments) adds a full-screen pass. Test on a laptop iGPU in a browser.
- Fog and gradients band, because there is no debanding. Add dither or noise in materials.
- Shaders compile the first time they're seen, which stutters. Show every material for one frame while the screen is black after a scene change.
- `vertex_color_is_srgb` does nothing in Compatibility. Check vertex-coloured models in the engine.
- Shadowed lights render in sRGB, so they can look brighter or darker than unshadowed ones. Adjust energy by eye.

## Export

- Single-threaded build (`variant/thread_support=false`), no PWA, exported as `index.html`. Leave itch's SharedArrayBuffer option off.
- Every machine needs the **4.7.2** Web export templates. Templates from another version fail.
- Expect about 10 MB of engine download plus the `.pck`. itch gzips the files itself.
- The single-threaded build runs everything on the main thread: `load_threaded_request` blocks, so a loading bar would jump from 0 to 1. Load while the screen is black.
- The game pauses while its browser tab is hidden.

## Audio

- Browsers start audio only after a click or key press. Start music in response to the player's first click (the web start overlay); never at boot.
- Web audio uses **Sample** playback. Bus effects (reverb, filters), procedural audio and reliable positional audio are unavailable. Bus volume and mute work.

## Saving

- `user://` is stored in the browser's IndexedDB, written in the frame after a file is **closed**. Closing the tab triggers no save.
- Save on every change, never on quit: write with `ConfigFile.save()` or a `FileAccess` you close.
- Saves are best effort. Incognito mode, blocked third-party storage (itch runs the game in an iframe) or a change of hosting domain loses them. When `OS.is_userfs_persistent()` is false, keep going for the session.

## Fullscreen and pointer

- itch's embed fullscreen button handles fullscreen.
- Fullscreen and mouse capture work only when requested inside an input event, such as a `Button` press.
- The stretch mode is `canvas_items` with `expand` at 1152×648, so UI scales in fullscreen and mouse-motion `relative` stays in content units.

## Still unverified in a browser

Check these in the soft-look prototype: stencil outlines on WebGL 2, audio with itch's "Click to Play", saves inside the itch iframe in Chrome, Firefox and Safari, and whether 3D at full resolution in fullscreen is too slow on HiDPI laptops.

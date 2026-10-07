# What can Godot 4.7's Compatibility renderer do for a soft 3D look on the web, and what are the itch.io web export gotchas?

Type: research
Status: resolved
Blocked by:

## Question

The game is cosy 3D with a soft/cute look, exported to the web (itch.io), so it runs on the Compatibility (WebGL2) renderer in Godot 4.7.2. Find out from primary sources (Godot docs, source, release notes):

- Which 3D rendering features Compatibility supports vs Forward+ in 4.7 (glow/bloom, fog incl. volumetric, SSAO/SSIL, SDFGI/VoxelGI/LightmapGI, shadows, tonemapping, adjustments, MSAA/FXAA/TAA, light count limits, custom shaders incl. screen-reading/post-process).
- What's realistic for a "soft" look in Compatibility (toon/soft shading, baked lighting, shader fog, outlines).
- Is there any WebGPU / Forward+ on web in 4.7?
- Web export gotchas for itch.io: threads vs no-threads export and SharedArrayBuffer/COOP-COEP on itch.io, audio playback before user interaction, `user://` persistence (IndexedDB) and when it flushes, export size, browser performance pitfalls.

## Answer

- Web is Compatibility (WebGL2) only. 4.7 has no WebGPU, so Forward+ can't run on web (WebGPU is still an open proposal).
- Usable for a soft look: glow (simplified), depth/height fog with sun scatter, SSAO (simplified, since 4.6), AgX/Filmic tonemap, adjustments with a 3D LUT, MSAA 3D, Toon or custom `light()` shading, Grow/Stencil outlines, rendering of baked LightmapGI (baking needs a Vulkan/D3D12/Metal GPU), untextured AreaLight3D.
- Not available: volumetric fog, SSR, SSIL, SDFGI, VoxelGI, DOF, decals, FXAA/SMAA/TAA, debanding (so fog and gradients will band). Limit of 8 omni + 8 spot lights per mesh, and shadowed lights render multi-pass.
- Export no-threads (`variant/thread_support=false`, the default; PWA off). Don't tick itch's experimental SharedArrayBuffer option. CI and teammates need the exact **4.7.2** Web templates (4.7.1 templates fail). Engine wasm is about 39.5 MB raw / about 10 MB gzipped, and itch gzips `.wasm`/`.pck` itself.
- `user://` saves reach IndexedDB asynchronously on the frame after a written file is *closed*. Nothing flushes on tab close, so save on state change. Saves are best-effort inside itch's iframe.
- Audio: Godot resumes the AudioContext by itself on the first click, key or touch. Start music after a click on the title screen, and keep the default Sample playback (no bus AudioEffects on web).

[findings](../research/01-web-renderer-and-export-limits.md)

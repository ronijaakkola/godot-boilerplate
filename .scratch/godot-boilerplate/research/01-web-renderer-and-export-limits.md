# Research: Compatibility renderer and web export limits (Godot 4.7.2, itch.io)

Answers [issue 01](../issues/01-web-renderer-and-export-limits.md). Researched 2026-10-07.

**Sources and version labels.** Docs come from the `4.7` branch of [godot-docs](https://github.com/godotengine/godot-docs/tree/4.7) (published at `docs.godotengine.org/en/4.7`). Source comes from the [`4.7.2-stable`](https://github.com/godotengine/godot/tree/4.7.2-stable) tag. Every claim below is confirmed for **4.7 / 4.7.2** unless it carries one of these labels:
- **[4.7.1]**: measured on the 4.7.1 export templates, which are the ones installed locally.
- **[older]**: only documented for an earlier 4.x.
- **[unverified]**: could not be confirmed from a primary source.

Shorthand: `SRC` = `https://github.com/godotengine/godot/blob/4.7.2-stable`, `DOCS` = `https://docs.godotengine.org/en/4.7`.

---

## 1. Compatibility vs Forward+ feature support (4.7)

The web platform supports only Compatibility. Mobile and Forward+ show "❌ No" for web ([renderers: overall comparison](https://docs.godotengine.org/en/4.7/tutorials/rendering/renderers.html#overall-comparison)). The project setting `rendering/renderer/rendering_method.web` defaults to `"gl_compatibility"`, so a Forward+ project silently drops to Compatibility on web ([ProjectSettings](https://docs.godotengine.org/en/4.7/classes/class_projectsettings.html#class-projectsettings-property-rendering-renderer-rendering-method-web)).

All rows below come from the [4.7 feature comparison](https://docs.godotengine.org/en/4.7/tutorials/rendering/renderers.html#feature-comparison) unless another link is given.

| Feature | Compatibility (web) | Forward+ | Notes |
|---|---|---|---|
| Glow / bloom | ✔️ | ✔️ | Simpler implementation. Compatibility hides `glow_levels/*`, `normalized`, `strength`, `blend_mode`, `mix` and `map`, and always uses Screen blend ([env docs: glow](https://docs.godotengine.org/en/4.7/tutorials/3d/environment_and_post_processing.html#glow), [Environment.glow_blend_mode](https://docs.godotengine.org/en/4.7/classes/class_environment.html#class-environment-property-glow-blend-mode)) |
| Depth and height fog | ✔️ | ✔️ | Sun Scatter and Aerial Perspective uniforms exist in the GLES3 scene shader ([SRC drivers/gles3/shaders/scene.glsl#L205-L222](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/gles3/shaders/scene.glsl#L205-L222)) |
| Volumetric fog / FogVolume | ❌ | ✔️ | Docs suggest faking it with quads, which "work with any rendering method" ([volumetric fog](https://docs.godotengine.org/en/4.7/tutorials/3d/volumetric_fog.html#faking-volumetric-fog-using-quads)) |
| SSAO | ✔️ (since 4.6) | ✔️ | A simplified SSAO. Only **Radius** and **Intensity** apply ([env docs: SSAO](https://docs.godotengine.org/en/4.7/tutorials/3d/environment_and_post_processing.html#screen-space-ambient-occlusion-ssao)) |
| SSIL, SSR, SDFGI, VoxelGI | ❌ | ✔️ | Forward+ only |
| LightmapGI | ⚠️ renders | ✔️ | "Rendering of baked lightmaps is supported. Baking requires hardware with RenderingDevice support." |
| ReflectionProbe | ✔️, 2 per mesh | unlimited | |
| Tonemapping | ✔️ | ✔️ | AgX is implemented in the GLES3 tonemapper ([SRC tonemap_inc.glsl#L115](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/gles3/shaders/tonemap_inc.glsl#L115)) |
| Adjustments (BCS, 1D/3D LUT color correction) | ✔️ | ✔️ | |
| Auto exposure, DOF blur | ❌ | ✔️ | ([env docs](https://docs.godotengine.org/en/4.7/tutorials/3d/environment_and_post_processing.html#auto-exposure)) |
| Debanding | ❌ | ✔️ | Compatibility has "the lowest [color precision] of all rendering methods" ([color banding](https://docs.godotengine.org/en/4.7/tutorials/3d/3d_rendering_limitations.html#color-banding)) |
| MSAA 3D | ✔️ | ✔️ | MSAA 2D is ❌ |
| FXAA, SMAA, TAA, FSR2 | ❌ | ✔️ | ([3D antialiasing](https://docs.godotengine.org/en/4.7/tutorials/3d/3d_antialiasing.html), [`screen_space_aa` note](https://docs.godotengine.org/en/4.7/classes/class_projectsettings.html#class-projectsettings-property-rendering-anti-aliasing-quality-screen-space-aa)) |
| SSAA (via resolution scale) | ✔️ | ✔️ | |
| OmniLight / SpotLight limits | 8 omni + 8 spot **per mesh**, 32 positional lights per frame | 512 per cluster | Raise or lower with `rendering/limits/opengl/max_lights_per_object` and `max_renderable_lights`. The docs advise lowering them on web ([ProjectSettings](https://docs.godotengine.org/en/4.7/classes/class_projectsettings.html#class-projectsettings-property-rendering-limits-opengl-max-lights-per-object), [lights & shadows](https://docs.godotengine.org/en/4.7/tutorials/3d/lights_and_shadows.html)) |
| DirectionalLights | 8 | 8 | |
| Shadows | ✔️, multi-pass | ✔️ | Shadowed lights render in sRGB space instead of linear, so they can look different from unshadowed ones. You may need to adjust energy ([lights & shadows](https://docs.godotengine.org/en/4.7/tutorials/3d/lights_and_shadows.html)). PCF soft filtering exists (`SHADOW_MODE_PCF_5/13`, [SRC rasterizer_scene_gles3.cpp#L3646](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/gles3/rasterizer_scene_gles3.cpp#L3646)). PCSS is ❌ |
| AreaLight3D (new in 4.7) | ✔️, untextured | ✔️ | "Textured area lights are not supported in the Compatibility renderer." Marked the most expensive light type ([area light](https://docs.godotengine.org/en/4.7/tutorials/3d/lights_and_shadows.html#area-light), [4.7 release](https://godotengine.org/releases/4.7/)) |
| Light projector textures, decals, particle trails, SSS | ❌ | ✔️ | |
| Custom shaders: `hint_screen_texture`, `hint_depth_texture` | ✔️ | ✔️ | In 3D the screen texture is copied after the opaque pass, so transparent objects are not in it ([screen-reading shaders](https://docs.godotengine.org/en/4.7/tutorials/shaders/screen-reading_shaders.html)) |
| Normal/roughness buffer | ❌ | ✔️ | Rules out normal-based screen-space edge detection |
| Post-processing via full-screen quad | ✔️ | ✔️ | |
| CompositorEffects, compute shaders | ❌ | ✔️ | |
| Color buffer | RGBA8 per docs | RGBA16F | See the source note below |

**Source note on color precision and glow (4.7.2).** Opaque, non-HDR render targets in GLES3 are allocated as `GL_RGB10_A2` ([SRC texture_storage.cpp#L2566-L2572](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/gles3/storage/texture_storage.cpp#L2566-L2572)). When glow is on, the renderer applies `luminance_multiplier = 0.25` to "fake a little HDR" so that bright and emissive values can bloom ([SRC rasterizer_scene_gles3.cpp#L2465-L2467](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/gles3/rasterizer_scene_gles3.cpp#L2465-L2467)). Turning on glow, SSAO or adjustments switches Compatibility to an extra internal buffer plus a post pass ([SRC #L2420](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/gles3/rasterizer_scene_gles3.cpp#L2420)). That pass costs fill rate on low-end GPUs. The docs table's "RGBA8" understates this slightly. Either way, it is low dynamic range.

**Material caveat.** `BaseMaterial3D.vertex_color_is_srgb` has no effect in Compatibility ([class ref](https://docs.godotengine.org/en/4.7/classes/class_basematerial3d.html#class-basematerial3d-property-vertex-color-is-srgb)). This matters for vertex-coloured low-poly assets: authored colours may come out off and need a check in-engine.

## 2. What is realistic for a "soft" look in Compatibility

- **Toon or soft shading.** StandardMaterial3D's **Toon** diffuse and specular modes give "a hard cut for lighting, with smoothing affected by roughness" ([standard material](https://docs.godotengine.org/en/4.7/tutorials/3d/standard_material_3d.html#diffuse-mode)). They are compiled into the GLES3 shader (`DIFFUSE_TOON`, [SRC scene.glsl#L1639](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/gles3/shaders/scene.glsl#L1639)). Custom `light()` functions are supported too (`LIGHT_CODE_USED`, [SRC scene.glsl#L1575](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/gles3/shaders/scene.glsl#L1575)). A wrapped or ramped diffuse in a spatial shader is therefore fully available on web.
- **Baked lighting.** LightmapGI *renders* in Compatibility, but baking needs a RenderingDevice GPU (Vulkan, D3D12 or Metal) ([renderers: GI](https://docs.godotengine.org/en/4.7/tutorials/rendering/renderers.html#global-illumination)). In practice you bake in the editor on a dev machine (a Mac with Metal works). Headless CI cannot bake. Lightmaps also need UV2 and are static.
- **Ambient and fill.** A constant or sky ambient, plus one DirectionalLight (shadowed) and a few unshadowed omni lights, keeps the light count well under the 8-per-mesh limit. **SSAO** (radius and intensity only) adds contact softness. AreaLight3D gives soft rectangular light, but the docs call it the most expensive light type, so use it sparingly on web.
- **Fog.** Depth and height fog with Sun Scatter and Aerial Perspective are available. Volumetric fog is not, so use quad sprites for local mist. Fog gradients will band, because Compatibility has no debanding. The docs suggest baking noise into textures or a [custom material debanding shader](https://github.com/fractilegames/godot-gles2-debanding-material) ([color banding](https://docs.godotengine.org/en/4.7/tutorials/3d/3d_rendering_limitations.html#color-banding)).
- **Glow and colour grading.** Glow works (simplified, Screen blend). Adjustments plus a 3D LUT for a pastel grade work, applied after tonemapping ([adjustments](https://docs.godotengine.org/en/4.7/tutorials/3d/environment_and_post_processing.html#adjustments)).
- **Outlines.** There are two cheap built-in options. One is **Grow** on a next-pass material with Cull Front, unshaded. The other is the **Outline stencil mode** (since 4.5) ([standard material: grow, stencil](https://docs.godotengine.org/en/4.7/tutorials/3d/standard_material_3d.html#stencil)). Stencil-mode parsing exists in the GLES3 material storage ([SRC material_storage.cpp#L3102](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/gles3/storage/material_storage.cpp#L3102)). Both need smooth-shaded, connected meshes. Stencil materials draw in the transparent pass. Screen-space outlines can only use depth (no normal buffer). **[unverified]** I found no explicit doc line saying stencil works on WebGL2. The GLES3 code path exists, but test it in a browser.
- **Antialiasing.** MSAA 3D is the only edge AA on web (no FXAA, SMAA or TAA). It is the default choice for a clean, soft look. SSAA (render scale > 1) is the expensive alternative.

## 3. WebGPU / Forward+ on web in 4.7?

**No.** "Godot 4 can only target WebGL 2.0 (using the Compatibility rendering method)… Godot currently does not support WebGPU, which is a prerequisite for allowing Forward+/Mobile to run on the web platform" ([web export: WebGL version](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#webgl-version)). The 4.7.2 `drivers/` directory has `gles3`, `vulkan`, `d3d12` and `metal`, and no WebGPU driver ([SRC drivers/](https://github.com/godotengine/godot/tree/4.7.2-stable/drivers)). The [4.7 release page](https://godotengine.org/releases/4.7/) lists no web-rendering changes. WebGPU is still an open proposal ([godot-proposals#6646](https://github.com/godotengine/godot-proposals/issues/6646)).

## 4. Web export gotchas for itch.io

### Threads vs no-threads, SharedArrayBuffer, COOP/COEP
- Single-threaded export has been the default since 4.3. It "is more compatible overall with stores like itch.io". It "cannot use threads, and is not as performant", but needs no cross-origin isolation ([web export note](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html); background in the [4.3 web progress report](https://godotengine.org/article/progress-report-web-export-in-4-3/#single-threaded-web-export) **[older]**).
- In 4.7.2 the export option `variant/thread_support` defaults to `false` ([SRC export_plugin.cpp#L375](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/export/export_plugin.cpp#L375)). It selects the `nothreads` feature tag ([#L357-L360](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/export/export_plugin.cpp#L357-L360)) and the `web_nothreads_*.zip` templates.
- Threaded builds need `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`. Without them, "the project will not run". The PWA service worker can fake these headers ([serving the files](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#serving-the-files)). However, PWA caching "currently lacks an automated cache busting mechanism" ([troubleshooting](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#troubleshooting)), which is risky with auto-deploy.
- itch.io offers an opt-in **"SharedArrayBuffer support — (Experimental)"** embed option. It sets COOP/COEP/CORP headers, breaks third-party iframes on the page, and moved games to the `html.itch.zone` domain. Per itch staff (leafo), Firefox launched these games in a popup window until about late June 2026. Safari **still** does ("It's still required for Safari", posted about 105 days before 2026-10-07) ([itch.io forum thread](https://itch.io/t/2025776/experimental-sharedarraybuffer-support)). This is not in itch's formal docs. The dates are relative forum timestamps.

### Audio before user interaction
- Since 4.3, web audio defaults to **Sample** playback through the Web Audio API (`audio/general/default_playback_type.web` = Sample). Sample mode does not support AudioEffects, reverb/doppler or procedural audio, and positional audio may be unreliable. Forcing **Stream** "may cause high audio latency and crackling" ([web export: audio playback](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#audio-playback), [ProjectSettings](https://docs.godotengine.org/en/4.7/classes/class_projectsettings.html#class-projectsettings-property-audio-general-default-playback-type-web)). This fits the map's ambient-plus-SFX audio.
- Browsers block autoplay. The docs advise asking the player to click or press a key, e.g. on a splash screen ([web export: audio](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#audio)).
- Godot resumes the suspended AudioContext **automatically** on the first key, mouse button, touch or IME event. `DisplayServerWeb` calls `OS_Web::resume_audio()` from those callbacks ([SRC display_server_web.cpp#L189](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/display_server_web.cpp#L189), [#L306](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/display_server_web.cpp#L306), [#L766](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/display_server_web.cpp#L766), [#L894](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/display_server_web.cpp#L894); [audio_driver_web.cpp#L162-L165](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/audio_driver_web.cpp#L162-L165)). No JavaScriptBridge code is needed.
- itch.io uses "Click to Play" by default and warns that "audio may be muted on some browsers when using auto-start" ([itch HTML5 docs](https://itch.io/docs/creators/html5)). **[unverified]** Two things: (a) whether the itch launch click counts as a gesture inside the game iframe, and (b) whether sounds started while the context is suspended play once it resumes or are lost. Both need a browser test.

### `user://` persistence (IndexedDB) and when it flushes
- `user://` is persisted to IndexedDB only if the user allows cookies/IndexedDB. **Third-party cookies must be enabled** when the game runs in an iframe, which is the case on itch. Incognito mode prevents persistence. `OS.is_userfs_persistent()` "can give false positives in some cases" ([web export: cookies](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#using-cookies-for-data-persistence)).
- **Flush mechanics (4.7.2 source):**
  1. Closing a `FileAccess` that was opened for WRITE under the user FS sets `idb_needs_sync` ([SRC os_web.cpp#L227-L243](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/os_web.cpp#L227-L243)). Removing a file does the same.
  2. At the start of the **next main-loop iteration**, if persistence is available and no sync is in flight, it calls `FS.syncfs(false)`. That call is **asynchronous** ([SRC os_web.cpp#L78-L90](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/os_web.cpp#L78-L90), [library_godot_os.js#L191-L206](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/js/libs/library_godot_os.js#L191-L206)).
  3. A final sync runs only on an engine-initiated quit (`finish_async`, [library_godot_os.js#L255-L270](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/web/js/libs/library_godot_os.js#L255-L270)). I found no `beforeunload`, `visibilitychange` or `pagehide` handler in `platform/web`, so closing the tab does not trigger a flush.
  4. `JavaScriptBridge.force_fs_sync()` exists, but the docs say it is "only useful for modules or extensions that can't use FileAccess to write files" ([class ref](https://docs.godotengine.org/en/4.7/classes/class_javascriptbridge.html#class-javascriptbridge-method-force-fs-sync)).
- When itch.io moved to `html.itch.zone`, existing local saves stopped being reachable ([itch forum](https://itch.io/t/2025776/experimental-sharedarraybuffer-support)). Saves are tied to the hosting origin.
- **[unverified]** How browser storage partitioning (Safari ITP, Chrome third-party storage partitioning) affects IndexedDB inside the itch iframe was not researched. Treat saves as best-effort.

### Export size
- Measured locally **[4.7.1]** with the `web_nothreads_release` template: `godot.wasm` is **39.5 MB raw, about 10.1 MB gzip -9, about 6.9 MB brotli -q11**, and `godot.js` is 280 KB raw / 68 KB gzip. The project `.pck` comes on top of that. The 4.7.2 templates were not measured but should be similar.
- Godot docs: the wasm "compresses particularly well, down to around a quarter of its original size with gzip". They list itch.io among "hosts that don't provide on-the-fly compression" ([serving the files](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#serving-the-files)). **Conflict:** itch.io's own docs say its CDN "will automatically apply GZIP compression" to `html, js, css, svg, wasm, wav, glb, pck` ([itch HTML5 docs: compressed file types](https://itch.io/docs/creators/html5)). itch owns that claim, so trust it. The Godot docs line looks stale.
- itch limits: at most 1,000 files, 500 MB total extracted, 200 MB per file, 240-character paths. The zip must contain `index.html` ([itch HTML5 docs](https://itch.io/docs/creators/html5)). Godot also recommends exporting as `index.html` and not renaming the exported files ([export file name](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#export-file-name)).
- To shrink the wasm further you need a custom template compiled with features disabled ([web export: mobile considerations](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#mobile-considerations)). That is probably not worth it for a jam.
- **Template version must match exactly.** Godot 4.7.2 looks for `export_templates/4.7.2.stable/web_nothreads_release.zip`. A local headless export with only 4.7.1 templates installed failed with "No export template found at the expected path". 4.7 adds per-platform template downloads, so only the Web templates need fetching ([4.7 release: export](https://godotengine.org/releases/4.7/)).

### Browser performance pitfalls
- **Shader compile stutter.** Ubershaders and pipeline precompilation don't exist in Compatibility. "To avoid shader stutters in Compatibility… preload materials, shaders, and particles by displaying them for at least one frame in the view frustum when the level is loading" ([pipeline compilations](https://docs.godotengine.org/en/4.7/tutorials/performance/pipeline_compilations.html)).
- Compatibility has a "low base cost, but high scaling cost" ([renderers](https://docs.godotengine.org/en/4.7/tutorials/rendering/renderers.html#overall-comparison)). WebGL driver validation makes draw calls costly ([GPU optimization](https://docs.godotengine.org/en/4.7/tutorials/performance/gpu_optimization.html)). Lowering `max_renderable_elements` and `max_renderable_lights` "may decrease shader compile times, particularly on web" ([ProjectSettings](https://docs.godotengine.org/en/4.7/classes/class_projectsettings.html#class-projectsettings-property-rendering-limits-opengl-max-renderable-elements)).
- The no-threads build runs everything on the main thread.
- The game pauses when its tab is inactive (`_process` stops) ([background processing](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#background-processing)).
- Safari "has several issues with WebGL 2.0 support"; Chromium and Firefox are recommended ([WebGL version](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#webgl-version)).
- Fullscreen and mouse capture must be requested from inside an input event callback ([full screen and mouse capture](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#full-screen-and-mouse-capture)).
- Serve `.wasm` as `application/wasm` ([serving the files](https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html#serving-the-files)).

---

## Implications for the boilerplate

1. **Renderer.** Set `rendering/renderer/rendering_method="gl_compatibility"` for the whole project so the editor shows what web players get. Set `rendering/anti_aliasing/quality/msaa_3d` to 2x or 4x, because it is the only AA on web. Leave `screen_space_aa` off, since it is ignored.
2. **Export threads setting.** Web preset with `variant/thread_support=false`, `variant/extensions_support=false` and `progressive_web_app/enabled=false`. PWA's service worker has no cache busting, which conflicts with deploy-on-push. Do **not** tick itch's experimental SharedArrayBuffer option, because a nothreads build doesn't need it and it forces a Safari popup. Export as `index.html`. Upload uncompressed, since itch gzips `.wasm`/`.pck` itself. CI and every teammate must install the **4.7.2** Web templates (`web_nothreads_release.zip`), because 4.7.1 templates fail. Expect a download of about 10 MB of engine plus the `.pck`.
3. **Environment for a soft look** (all confirmed available in Compatibility):
   - Tonemap AgX (or Filmic)
   - Ambient from sky or a constant pastel colour
   - SSAO (radius and intensity only) for contact softness
   - Glow with a low threshold for soft bloom on emissives (Screen blend)
   - Depth and height fog with Sun Scatter for atmosphere
   - Adjustments plus a small 3D LUT for a pastel grade
   - One shadowed DirectionalLight with soft PCF filter quality, and a few unshadowed omni lights (≤8 per mesh)
   - Toon diffuse, or a custom `light()` ramp, in materials
   - Outlines via Grow next-pass or Stencil Outline
   - Optional: LightmapGI baked on a dev machine

   Avoid: volumetric fog, SSR, SSIL, SDFGI, VoxelGI, DOF, decals, FXAA/SMAA/TAA, textured area lights, and anything that needs the normal buffer. Each post effect in the stack forces an extra full-screen pass, so budget them and test in a browser on a laptop iGPU. Plan for banding in fog and gradients (no debanding): add dither or noise in materials. Warm up materials on the loading screen to avoid shader-compile hitches.
4. **Persistence flush approach.** Save on state changes, not on exit. Write with `ConfigFile.save()` or `FileAccess`, and make sure the file is **closed** (`close()`, or let the `FileAccess` go out of scope). The engine then flushes to IndexedDB asynchronously on the next frame. Never rely on `NOTIFICATION_WM_CLOSE_REQUEST` or tab close to save on web. No `force_fs_sync()` is needed from GDScript. Treat saves as best-effort: check `OS.is_userfs_persistent()` and degrade gracefully, since incognito or blocked third-party storage loses data.
5. **Audio unlock approach.** Rely on Godot's built-in resume on first input. Open the game on a title or main-menu screen that needs one click ("Click to start"), and start music in response to that click rather than at boot. That avoids the unverified question of whether sounds queued while suspended play later. Keep the default **Sample** playback type, and do not design around bus AudioEffects (reverb, filters) on web.
6. **Open items to verify in the soft-look prototype** (browser test on itch): stencil outlines on WebGL2, audio behaviour with itch's Click-to-Play, IndexedDB persistence across reloads inside the itch iframe in Chrome, Firefox and Safari, and the actual 4.7.2 wasm and `.pck` size.

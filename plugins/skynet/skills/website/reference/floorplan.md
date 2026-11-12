# Floor plans and the 3D view

Read this when a page shows the layout of a building: a home model, a listing, an office, a venue. Worked example in [site/](site/REFERENCE.md): the `Plan` page (`codes/Plan.cs`, `scripts/Plan.js`, `styles/Plan.css`, prefix `pl-`) is the viewer, `scripts/three.min.js` is three.js (MIT licence, tested with this viewer), the classes `FloorPlan`, `PlanFloor`, `PlanRoom` and `PlanOpening` are in the model file, and `CleanPlan` with `SavePlan` in `codes/AdminThings.cs` is the staff-side check. Copy the `fp` functions, the section markup and the `pl-fp`/`pl-seg` styles into the page that shows the plan, rename `pl-` and `PlanJs`, and keep the rest as it is.

## Data

- A plan is one or more **floors**; a floor has **rooms** (name, kind, `X`, `Y`, `W`, `H` in feet from the top-left corner of the building) and **openings** (`door`, `window` or `open` for a wide gap, a position, a length and `h` or `v` for the direction of the wall).
- Room kinds decide the colour, the stairs drawing and the low balcony walls in 3D: living, dining, kitchen, bed, bath, office, entry, hall, stairs, closet, laundry, garage, balcony (`Kinds` in the C#, `FP_COL` in the JS: change both together).
- The plan is stored with the thing it belongs to (`HomeModel.Plan`), in `site.json`. The page sends it to the browser once, as JSON in `data-plan` on the section.
- The staff editor sends the whole plan as one JSON value (`plan`). `CleanPlan` checks it before saving: known kinds, sizes and positions clamped to sensible limits, short names, and no two rooms on one floor overlapping. A refused plan names the floor and the rooms.

## Viewer

- **2D first.** The section opens on the 2D plan (SVG, drawn in the browser from the data), which works everywhere and prints. Tapping a room shows its name and size; the list under the plan does the same.
- **3D on request.** The **3D view** button loads `scripts/three.min.js` the first time it is pressed, so pages that never use it do not pay for it. It turns slowly until touched; drag turns it, the + and − buttons and a two-finger pinch zoom (the mouse wheel is left to scroll the page), tapping a room or its label shows its size, **Reset** returns to the start.
- No WebGL, or the script fails to load: the viewer stays on 2D without an error.
- Several floors: the floor buttons switch both views.

## Checks

- `scripts/three.min.js` must be in the project. A missing file comes back as the not-found page, and the 3D view silently never opens; `shots.js` reports a script that answers with a web page, but only once the page asks for it, so the interaction test must press **3D view**.
- The interaction test presses 3D, waits for `#pl-fp-3d[data-ready="1"]` (set after the first draw), presses anywhere on the view first (that stops the slow turn, so labels hold still), drags (the view must turn), taps a room (its size appears), switches floors, and returns to 2D.
- **The editor is the site's own work.** The reference ships the check, not a plan editor: write the staff form for the site (a table of rooms and one of openings per floor, with a live 2D preview drawn by the same `fpSvg`), send the plan as JSON to a method like `SavePlan`, and open it at 390 with a real plan.
- **Openings sit on a wall line.** `Dir` is the direction the opening runs: `h` along a horizontal wall (constant `Y`, from `X` to `X + Len`), `v` along a vertical wall (constant `X`, from `Y` to `Y + Len`). `X`/`Y` must be exactly on a room edge, or the opening floats in the room.
- `check_sources.py` accepts `three.min.js` because its first comment is a licence; do not strip it.

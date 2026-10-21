---
name: art
description: Paint original website artwork in code with Python (Pillow, NumPy, SciPy) - colour fields, misty landscapes, linocut seascapes and night cities, botanical watercolours, ink-wash mountains, still lifes, geometric and gestural abstraction, gallery-room banners and flat portraits - saved as WebP. Use when a SkyNet site needs images and stock photos are not wanted.
user-invocable: false
---

# Art painted in code

Every image comes from a seeded Python function, so it is original, repeatable and free to publish. Requirements: `pip install pillow numpy scipy`.

## Files

| File | Holds |
|---|---|
| [scripts/paint.py](scripts/paint.py) | `paint(spec, params)` and ten styles |
| [scripts/scenes.py](scripts/scenes.py) | `room_banner(works, ...)` gallery-wall banners, `portrait(params)` flat portraits |
| [scripts/example.py](scripts/example.py) | One working example per style; run it first to see what each style looks like |

```bash
cd ${CLAUDE_SKILL_DIR}/scripts && python3 example.py /path/to/output
```

## Painting one image

```python
import sys
sys.path.insert(0, "<skill folder>/scripts")
import paint
im = paint.paint(dict(style="landscape", seed=22, size="90 × 150 cm"), params)
im.save("images/works/six-ridges.webp", "WEBP", quality=84, method=6)
```

- `size` is "height × width" in any unit; the long side becomes 1400px.
- `seed` changes the composition; keep it fixed so the image can be rebuilt.
- Save a full image (1400px) and a thumbnail (`thumbnail((640, 640))`).

## Styles and their parameters

Copy the matching entry from `example.py` and change colours and numbers.

| Style | Looks like | Main parameters |
|---|---|---|
| `colorfield` | soft stacked colour rectangles | `ground`, `rects` [((x0, y0, x1, y1), colour)], `glow`, `feather`, `axis` |
| `landscape` | layered misty hills, optional lake, sun, rain | `sky0`, `sky1`, `layers` (far to near), `horizon`, `top`, `water`, `sun` (x, y, r, colour), `haze`, `mist`, `mistamt`, `rain` |
| `linosea` | linocut sea with pier and lighthouse | `light`, `mid`, `dark`, `lamp` |
| `linowave` | linocut rolling wave | `light`, `mid`, `dark` |
| `linocity` | linocut night street with tram, or a facade of windows (`scene="facade"`) | `night`, `yellow`, `red`, `mid` |
| `botanical` | ink and watercolour plants; `kind` = fern, garlic, seeds, quince; `night=True` for gouache on black | per kind: `green`, `green2`, `dark`, `petal`, `fruit`... |
| `inkwash` | ink mountains, mist, pines, boats, red seal; `kind` = mountain, river, pines, ferry | `kind` |
| `stilllife` | table, wall, cloth and lit objects (jug, vase, bowl, cup, pear, lemon, orange) | `wall0`, `wall1`, `table`, `tablec`, `cloth`, `clothc`, `objs` |
| `geometric` | flat shapes on a grid; `kind` = grid, moons, market, bands | `grid`, `bg`, `pal` |
| `gestural` | big bristle brush strokes and marks | `bg`, `pal`, `n`, `marks`, `splat`, `turn`, `kind="pull"` |

## Banners and portraits

```python
import scenes
banner = scenes.room_banner([(img1, False), (img2, True), (img3, False)], wall="#E9E1D6", floor="#BFA88C", visitor="#7E3B2B")
face = scenes.portrait(dict(bg="#D6E2CC", skin="#D9A985", hair="#2E2420", style="bun", cloth="#4F7A43", glasses=True))
```

- `room_banner` hangs two or three images on a gallery wall with light pools, a bench and visitor silhouettes (1600×760). `True` frames a work with a mat (for paper works). Keep the left third empty for headline text.
- `portrait` draws a faceless editorial portrait. `style`: long, bob, short, bun, crop, fade, curly; optional `beard`, `glasses`, `stripes`, `dots`.

## Working method

1. Plan the set: how many images, which styles, a palette that matches the site.
2. Paint a first batch and make a contact sheet (paste thumbnails onto one image) and **look at it**.
3. Fix what looks wrong: change the seed for a different composition, adjust colours, sizes and positions. Repeat until every image is good.
4. Then check each image **at its thumbnail size** (640px and the card size the page uses): every object must still read as what it is. A light object on a light ground (a white tub on pearl tiles, a cream sofa on a sand wall) needs a cast shadow, a darker rim or an outline; otherwise it is a blob. Repaint the set, not the one image, so the set stays consistent.
5. Save WebP: works about 1400px, thumbnails 640px, banners 1600px, portraits 480px.

## Rules

- Never imitate a specific famous artwork, character, logo or living artist's signature work; paint generic styles with your own compositions and colours.
- No text inside images; headings belong in HTML.
- Use `loading="lazy"` for images below the first screen.

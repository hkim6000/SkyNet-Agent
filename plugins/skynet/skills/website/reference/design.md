# Design rules

## Plan first

Agree on these before writing code:

- **Brand:** an invented name, a one-line idea, a palette (ink, background, paper, line, accent, one or two supporting colors) and two fonts (display + text) with solid fallbacks.
- **Pages:** name, two-letter prefix, purpose, server methods.
- **Data:** what goes into `data/site.json` (or which SQL tables).
- **Demo behaviour:** what is real (validation, prices, filtering) and what is simulated (accounts, payments, uploads).
- **Images:** how many and in what style (the `art` skill).

## Layout

- Content width about 1240px with 28px side padding (16px on phones).
- Sticky header: logo, menu, search, account; on tablets and phones a burger opens a slide-in menu with a scrim.
- Sections spaced 44 to 56px apart; one clear heading per section with a "See all" link where it helps.
- Cards: image, small eyebrow label, title, one or two lines of detail, actions.
- Footer: brand line, newsletter field, three link columns, a line stating the brand and data are fictional.
- A toast element for short confirmations.

## Responsive breakpoints

Check three widths: **1440** (desktop), **820** (tablet) and **390** (phone).

| Max width | Typical changes |
|---|---|
| 1180px | tighter menu spacing, 3 columns become 2 |
| 980px | slide-in menu, side panels drop below content, sticky panels become static |
| 680px | one column, 16px gutters, horizontal chip rows scroll, tables scroll inside a wrapper |

On phones, put the most important action near the top (for example the booking box before long text) using `order`. There must be no horizontal page scroll at any width.

## Interaction patterns that work well

- **Filters and tabs:** the server returns the new list; JS updates the URL with `history.replaceState` so the view can be shared.
- **Search suggestions:** debounce 250ms, minimum 2 characters, server returns up to 6-8 results and a "see all" link.
- **Forms:** one error element per field, filled by the server; a confirmation box after success; a clear "Demo" note when nothing is stored.
- **Viewer or modal:** open by id (`?w=key` deep link), Esc closes, arrow keys step, swipe on touch.
- **Carts and bookings:** the browser keeps the list; the server recalculates every price and checks every rule each time.

## Accessibility

- Real `<button>` for actions and `<a>` for navigation; `aria-label` on icon buttons.
- Every input has a `<label>`; errors are text, not only color.
- Visible focus states; keyboard support for menus, tabs and viewers.
- Alt text on content images; empty `alt=""` on decorative ones.
- Contrast: body text at least 4.5:1.

## Content rules

- Invent every brand, person, product, address and number. Use `.example` email domains and 555 phone numbers.
- No real trademarks, logos, famous artworks or characters.
- Reviews or testimonials only when clearly labelled as fictional demo content.
- No payment-card fields in demos; say "Demo: no payment taken".
- Write in plain, short sentences.

## Images

- WebP, sized for their slot (thumbnails about 640px on the long side, banners about 1600px wide).
- `loading="lazy"` on everything below the first screen.
- Paint artwork in code with the `art` skill instead of using stock photos.

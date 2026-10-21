# Design rules

## Plan first

Agree on these before writing code:

- **Brand:** an invented name, a one-line idea, a palette (ink, background, paper, line, accent, one or two supporting colors) and two fonts (display + text) with solid fallbacks.
- **Pages:** name, two-letter prefix, purpose, server methods.
- **Data:** what goes into `data/site.json` (or which SQL tables).
- **What is stored:** every form and action saves for real (messages, sign-ups, orders, bookings) in `data/*.json` or SQL; say where each one goes.
- **Images:** how many and in what style (the `art` skill).
- **Admin (if any):** staff roles and the areas each one manages. Read [admin.md](admin.md).

## Layout

- Content width about 1240px with 28px side padding (16px on phones).
- Sticky header: logo, menu, search, account; on tablets and phones a burger opens a slide-in menu with a scrim. The brand name stays visible and whole at 390px (public and admin); drop secondary items first. In the admin header at phone width hide the signed-in name and role (they are in the slide-in menu) and keep only the burger, the brand and Sign out.
- Admin "View site" links open in a new tab (`target="_blank" rel="noopener"`), so staff keep their place.
- Sections spaced 44 to 56px apart; one clear heading per section with a "See all" link where it helps.
- Cards: image, small eyebrow label, title, one or two lines of detail, actions.
- Footer: brand line, newsletter field, three link columns, a copyright line.
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
- **Forms:** one error element per field, filled by the server; the server saves the entry, then shows a confirmation box that says what happens next (*We will reply by email*).
- **Viewer or modal:** open by id (`?w=key` deep link), Esc closes, arrow keys step, swipe on touch.
- **Carts and bookings:** the browser keeps the list; the server recalculates every price and checks every rule each time.
- **Confirm before changing data:** an in-page dialog, never `window.confirm` (browsers can suppress it and it looks foreign). The title is the question (*Cancel this appointment?*), one line says what happens, the buttons are verbs (*Keep it* / *Cancel appointment*) with the risky one in red. Enter confirms; Esc, the backdrop and the left button step back; focus stays in the dialog and returns afterwards. An optional text field takes a reason, checked before closing. Ask for every action that changes data from a list, card or detail window (check in, move, cancel, delete, publish). A form with a Save button needs no extra question, but closing it or leaving the page with unsaved changes asks *Leave without saving?*. Code: [admin.md](admin.md#confirm-dialog).
- **Menu labels are nouns.** A top-menu or admin-menu entry names the thing the page is about (*Certificate*, *Orders*, *Service area*), never the action (*Verify*, *Book*, *Check*). Actions belong on buttons inside the page (*Check the code*). The page heading may be the action.
- **Text follows the record's current state.** Every sentence the page writes about a record must be true now, not when the event happened. An order refunded in full says "access ended" only while the enrollment is locked; once the student pays again it says so. A cancelled booking does not keep "we will call you". Build the sentence from the current records, not from the event alone.
- **Frame classes stay on the frame.** `xx-head`, `xx-nav`, `xx-foot` and `xx-site` belong to the page header, menu, footer and wrapper only. A card's own top or bottom is `xx-chead` or `xx-cfoot`; C# and JavaScript that write content never emit a frame class, or the content takes the frame's dark band and spacing. `check_sources.py` fails this.
- **Nothing clips.** Names in charts, bars, chips and cards wrap or shrink their box; never `Clip()` or `text-overflow: ellipsis` a name the reader needs. Chart label columns use `minmax(0, 40%)`, not a fixed width.
- **Admin lists on phones:** below 600px a table with more than three columns becomes a stack of cards (one record per card, label and value per line) instead of a side-scrolling table; nothing is cut off and nothing scrolls sideways.
- **Admin lists:** the server searches, filters and pages (`const int Size = 10` to `25`) and returns the rows plus a pager (*Page 1 of 11 · 273 appointments*). Search waits 250ms after typing; changing a filter goes back to page 1; saving an edit reloads the current page, not page 1; an empty result says *No services match.* Request keys must not equal query-string names (`term`, not `q`).

## Accessibility

- Real `<button>` for actions and `<a>` for navigation; `aria-label` on icon buttons.
- Every input has a `<label>`; errors are text, not only color.
- Visible focus states; keyboard support for menus, tabs and viewers.
- Alt text on content images; empty `alt=""` on decorative ones.
- Contrast: body text at least 4.5:1.

## Content rules

- Sample content (brand, products, services, team, address) is invented for the owner to replace. Use `.example` email domains and 555 phone numbers.
- No real trademarks, logos, famous artworks or characters.
- No invented reviews or testimonials; leave room for the owner's real ones.
- **Visit and order status follows the clock.** A booking can be checked in (arrived) only on its own day, marked no-show only after its start time, and marked done only after check-in; the server refuses the rest with a message, and the buttons for actions that are not yet allowed are not shown. Cancel is allowed any time before check-in.
- **Undo frees the source.** Voiding an invoice, cancelling an order or a booking, or declining a quote puts whatever it came from back where it was (the job returns to "To invoice", the slot opens again, the stock is released), so the next step can be done again. A message that says "create a new one" must point at something the user can do.
- **Pre-fill from the request.** What the customer chose (services, items, options) becomes the starting lines of the staff record (the quote, the order, the visit), at the list price, for staff to change. Staff never retype what the customer already typed.
- **Promise only what the site does.** No "we will email you", "you will get a text" or "your receipt is on its way" unless the site sends it, or the staff step that sends it is part of the flow. Say what happens instead: "we will call you", "keep this reference".
- **Rights in words.** Lists of staff show rights as area names and plain words ("Quotes: send, Jobs: edit"), never as letters such as VEX. The letters stay in the data and the grid.
- **Run-mode text only where it belongs.** The staff sign-in page may explain Demo mode while in Demo. Settings, Users, My account and the README do not describe Demo mode when the site runs in Production; write "Run mode is set in appConfig/application.cfg" and nothing more.
- No payment-card fields. Orders and bookings are saved as unpaid (pay on pickup, on arrival or by invoice) until the owner adds a payment provider. If the plan includes online payment, use the provider's hosted checkout page, keep the key in a server-side file the owner enters in Settings, confirm payment through the provider's signed webhook (plus a status check when the customer returns), and never cancel an unpaid card order without first asking the provider whether it was paid.
- **Every money call carries an idempotency key.** A charge, a refund or a payout sent to the provider carries a key built from the record ids and the amount (`Idempotency-Key: refund-<order>-<request>-<cents>` for Stripe), so a retry after a crash or a timeout cannot move the money twice. Mark the record "processing" before the call and settle or reopen it after; a request stuck in "processing" for more than five minutes may be decided again.
- **Customer accounts** (students, members, patients who sign in): the rules are in [accounts.md](accounts.md): two sign-in gateways, a phone number on sign-up, name and phone editable, a password change and an emailed reset link.
- Write in plain, short sentences.

## Images

- WebP, sized for their slot (thumbnails about 640px on the long side, banners about 1600px wide).
- **The Home hero shows the place.** For a business with premises (a school, salon, clinic, shop, hotel) the page top shows the building and its rooms, painted in code, not an abstract or a product still life. Offer a **slideshow** in the plan as a developer option ("Page top: one picture, or a slideshow of the building and rooms every 7 seconds?"); when the developer says yes, build it from [code/slideshow/](code/slideshow/) and give the Pages editor a Slides list.
- `loading="lazy"` on everything below the first screen.
- Paint artwork in code with the `art` skill instead of using stock photos.

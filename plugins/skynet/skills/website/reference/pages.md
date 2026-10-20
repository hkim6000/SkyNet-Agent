# Pages: block-edited page content

Read this when the owner must change the words and pictures of the public pages themselves. Instead of one admin form per text field, every public page is a **list of blocks** that staff edit in place on one admin page, **Pages**. This is the pattern of the sport-center template and the flower shop. Worked example (namespace `MySite`): [code/pages/](code/pages/) holds `Blocks.cs`, the four `AdminPages` files, `Renderer.cs.txt` (the renderer every public page carries, with `PX` for its prefix) and `blocks.css.txt` (the matching styles). Copy them and change the page list, the data parts, the icons and the seed.

## Data

```csharp
SiteData.Pages : Dictionary<string, PageDoc>      key = page key ("home", "about", ...)
PageDoc  { List<Block> Blocks; List<PageVersion> Versions; DateTime Saved; string By; }
Block    { Id, Type, Source, Hidden, Kicker, Title, Text (sanitized html), Media, Label, Link, Label2, Link2, Flip, Items }
BlockItem{ Icon, Media, Title, Text, Link, Label }
```

`Core/Blocks.cs` is the one shared file: the page list, the block types, the data parts, the sanitizer, the save-time check (`Clean`), `Ensure` (creates missing pages and required data blocks on every load, and seeds pages from any older per-field content the first time) and `Uses` (which pages use a media file).

### Page list and data parts

```csharp
Pages: home → Home [favourites, occasions, delivery]   shop → Shop [bouquetlist]   about → About []
       track → Track an order [trackform]              contact → Contact [contactform]
```

Pages are a fixed list in code (transactional pages such as Product, Cart and Pay are not block-edited). A **data part** (`Type = "data"`, `Source = key`) is the piece of a page that comes from the site's own data or is a form: the product list, the contact form, the booking box. Data parts must appear exactly once on their page; staff can move, hide and retitle them, not remove them. `Ensure` adds any that are missing.

### Block types (content blocks)

| Key | Name | Fields |
|---|---|---|
| hero | Page top | kicker, title, text, media, two buttons |
| text | Text | kicker, title, text |
| split | Picture and text | kicker, title, text, media, one button, flip |
| cards | Cards | kicker, title, text; items: icon, title, text, link |
| steps | Steps | kicker, title, text; items: title, text |
| stats | Numbers | kicker, title; items: title, text |
| boxes | Checklists | kicker, title; items: title, lines |
| people | People | kicker, title, text; items: media, title, text |
| faq | Questions | kicker, title; items: title, text |
| quote | Quote | quote, name, media (photo) |
| media | Picture or video | media, caption |
| cta | Call to action | kicker, title, text, two buttons |

Keep the icon list short and on-topic for the site (flower, leaf, gift, truck, clock, pin, calendar, heart, star, people, tick, phone, mail, card). `{name}` in any text shows the shop name from Settings.

## The admin page

One canvas, every block an inline editor (`.pg-blk`): header with a drag grip, the block name, a *From your data* badge, Hide/Show, up, down and (content blocks only) remove; body with `contenteditable` fields (`plaintext-only` for single lines, a rich-text `div.pg-er` for text with a floating Bold / Italic / Link / List / Clear toolbar), a media field (`.pg-em` with `data-src`, Change and Remove), button fields, and item lists with add / move / remove and a `<template>` for new items.

- Page tabs at the top; **Unsaved changes** marker; **Versions**, **View page** (new tab), **Save page**.
- Move, hide, remove and edits happen in the browser only; **Save** sends the whole list as JSON (`blocks`). The server runs `Blocks.Clean`: types allowed on that page, every required data part present once, ids well-formed, text sanitized to `p br b i ul ol li a`, links checked (`SafeLink`: a page name, `https://`, `mailto:`, `tel:`, `#anchor`), media paths present in the library (photos only where the field says so). A failed check returns a message and saves nothing.
- Each save keeps the previous version (last 5 per page, with who and when); **Restore** swaps one back and keeps the current one in the list.
- Drag uses pointer events on the grip (`grab`, `dragMove`, `dragEnd`), not HTML5 drag-and-drop, so it works on touch.
- Paste into a field inserts plain text. Switching page tabs or leaving with unsaved changes asks first. The picker is the one from [media.md](media.md), in single-choice mode.
- Read-only users see every editor disabled.

## The public pages

Each public page keeps its own copy of the renderer (per-page prefix, as always): `PageHtml(site, media, key)` walks the visible blocks and switches on type; `DataPart(site, b, first)` renders that page's own data parts, with the block's kicker, title and text as the part's heading. Only the first hero or data part on a page gets an `<h1>`. The HTML of such a page is just the header, `{plhd_blocks}` inside `<main>`, and the footer. The block classes live in the page's CSS (`blocks.css.txt` with `PX` replaced by the prefix).

Things to carry over from the old per-field pages when you switch a site to blocks:

- Shop details (name, tagline, phone, email, address, hours) move to **Settings**.
- Catalogue groupings with photos (occasions, categories) move to a tab on the catalogue admin page, with the single-choice picker.
- Contact messages get their own admin page, **Messages**, with its own menu item and unread badge.
- Write a `Legacy` seed that maps the old fields and blocks (hero text, promises, about paragraphs, care tips, FAQ) into blocks the first time, so an existing site loses nothing.

## Before delivering

- Each page shows its seeded blocks; moving, hiding, removing and adding a block changes the public page after Save; a page switch with unsaved changes asks.
- Save with a bad link (`javascript:`) is refused with a message; a missing data part is refused.
- Versions lists the live version and the old ones; Restore puts a previous version live.
- A video chosen in a Picture or video block plays on the public page; a photo chosen in Page top replaces the hero.
- 1440, 820 and 390 px on the public pages and on Pages itself, with no sideways scroll; the editor's two-column blocks stack on tablets.

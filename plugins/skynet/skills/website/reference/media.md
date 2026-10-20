# Media library

Read this when staff need to upload photos or videos and pick them for products, pages or people. It is one admin page plus one shared class, and every other admin page that needs a picture opens the same picker. Worked example (from a flower shop, namespace `MySite`): [code/media/](code/media/) holds `Media.cs` and the four `AdminMedia` files; copy them, rename the prefix and adjust `UsedBy`.

## Shape

| Part | Files |
|---|---|
| Shared C# | `codes/Core/Media.cs`: load and save the list, receive uploads, sniff file types, size limits, where a file is used, erase |
| Admin page | `AdminMedia` (prefix `am-`): upload, All / Photos / Videos chips, search, grid, edit dialog (alt text, note for staff, where used), delete |
| Data | `data/media.json`, one `MediaItem` per file: `Id, Path, Thumb, Kind (photo/video), Name, Alt, Caption, Bytes, Added, By` |
| Files | `images/uploads/<id>.<ext>`; existing painted images under `images/` are added to the list on first start (`Seed`), with their `-thumb.webp` when one exists |
| Rights | area `media`: View, Edit (upload, alt text), Extra = delete files |
| Settings | `MaxVideoMb` on `SiteData` (default 30, 1 to 100); a field in **Settings** changes it |

## Rules

- **Check by contents, not by name.** Read the first 16 bytes: JPG `FF D8 FF`, PNG `89 50 4E 47 0D 0A 1A 0A`, GIF `GIF87a/89a`, WebP `RIFF....WEBP`, MP4 `....ftyp` (not `qt`). The extension must match the sniffed type. Photos up to 8 MB, MP4 up to `MaxVideoMb`.
- **Receive multipart.** SkyNet posts every `<input type="file">` on the page with the request. Read them in C# with `Local.Accessor.HttpContext.Request.ReadFormAsync()` (`Media.Received()`), up to 20 files per request. Copy to a `.part` file and move into place; stop and delete the part file if the length lies. Raise the limits in `Program.cs` (`Kestrel MaxRequestBodySize`, `IISServerOptions.MaxRequestBodySize`, `FormOptions.MultipartBodyLengthLimit`, 110 MB) and in `web.config` (`maxAllowedContentLength`), and the README tells the owner to create `images/uploads/` and grant Modify.
- **Clear the file input after every upload** (`input.value = ''`), or the next request re-uploads it (pitfalls).
- **Deleting asks first, and refuses a file still in use.** `Media.UsedBy(site, path)` lists every place: pages, products, occasions, people, fixed files such as `images/hero.webp` or the About pictures. The delete button shows the toast *X is still used: ... Replace it there first.*
- **Thumbnails:** `Media.Thumb(path)` returns `name-thumb.webp` when it exists next to the file, otherwise the file itself. Cards and lists use it; a product page uses the full file.
- **Video previews** in admin grids use `<video src="file.mp4#t=0.1" muted preload="metadata" playsinline>` so a first frame shows; a play badge sits on top.
- **Alt text** is edited in the library and used wherever the file appears; a video gets `aria-label` instead.

## The picker, reused everywhere

Each admin page that needs a file has its own picker dialog (`xx-pick`), filled by a `Pick` method on that page that lists the library (photos only, videos only, or both), with search and an **Upload new** button that calls the page's own `Upload` and refreshes the grid.

- **Single choice** (a hero picture, an occasion photo, a person's portrait): clicking a tile sets a hidden input (`data-k`) and a preview, then closes.
- **Ordered multi-choice** (product photos and videos): tiles toggle and show their order number; **Use these** copies the list into a strip of thumbnails with ◀ ▶ ✕ buttons; the first item must be a photo because cards and the cart use it. The server checks every path against the library and the first item's kind.
- Keep one limit (6 items) and say it in the hint.

## Server-side check on save

Whatever the browser sends, the server re-validates: every path exists in `media.json`, the kind matches what the field allows, and at least one photo is present where a picture is required. Refuse with a field error, never save a dangling path.

## Before delivering

- Upload a JPG, a PNG and a short MP4; upload a renamed text file (`notes.jpg`) and a `.mov`: both refused with a clear message.
- Set the video limit to 1 MB in Settings; a 2 MB MP4 is refused and the message names the limit.
- Delete an unused file (gone from the grid and from disk); try to delete one in use (refused, names the place).
- Pick a photo for a product and a video as its second item; the product page shows the gallery and the video plays on click.
- Test uploads on the real framework once, not only on the verify stub: it is the one thing the offline preview cannot exercise.

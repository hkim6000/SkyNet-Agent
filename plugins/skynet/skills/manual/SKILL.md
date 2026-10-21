---
name: manual
description: Write a user manual for a finished SkyNet website - one self-contained HTML file with a side menu, search, screenshots and SVG diagrams, written for the people who run the site. Use when the user asks for a user manual, user guide or help document for a SkyNet site, or runs /skynet:manual.
argument-hint: "[site folder]"
---

# User manual for a SkyNet site

Site: `$ARGUMENTS` (default: the project in the current folder).

The result is **one HTML file** the owner can send to staff: a top bar, a side menu built from the chapters, a search box, chapters shown one at a time, screenshots that open full size on click, SVG diagrams, and it prints as one long document. Everything is inside the file; it opens offline.

Load the `skynet:website` skill (and `admin.md` if the site has a staff area) and the `skynet:verify` skill first.

## Rules

- **Real use.** Write for the clinic, shop or hotel that runs the site. Capture with `app.app.runmode | 1` on a copy of the project so the sign-in page and the admin look as they do in Production (step 2 lists the capture-only patches); the delivered project stays as it is. No sample passwords or invented staff logins in the text, and no password in any screenshot or diagram (mask it as `****-****-****`). The word "demo" appears nowhere; describe run mode only in Installation & Setup. Installation & Setup shows the first-sign-in box once; everywhere else people sign in with their own accounts.
- **One worked flow.** Walk the site's main flow end to end for the screenshots (request → record → each status → payment, or the site's equivalent), including one refused action, so every chapter shows a real record rather than an empty list.
- **Every fact from the code.** Before writing a sentence about a limit, a status, a right, a badge or a button, find it in the C# or JS. Write nothing from memory or from the README alone; when the code and the README disagree, the code wins.
- **Plain words, short sentences.** The reader is the front desk, not a developer. Name buttons in **bold** exactly as on screen. Use the site's own words (its Words settings).
- **Bugs found while capturing:** list them for the user with the fix you propose; change the site only when the user agrees, then recapture.

## Step 1 - Plan (no files yet)

Read the README, every admin page, `codes/Core/`, the settings page and the public pages. Then reply with:

- **Chapters:** Overview, Getting Started (sign in, layout, confirmations, rights, phone), one chapter per admin area in menu order, Settings, The Public Website, Installation & Setup, Reference, Quick Answers. Two to eight numbered topics (`3.2 Opening an appointment`) per chapter.
- **Diagrams (5 to 8):** how the pieces fit, the sign-in page with numbered callouts, the admin layout with lettered callouts, the main status flow, the main visitor flow, a rule the reader must understand (for example how free times are worked out), the first sign-in.
- **Screenshots:** a list of names (`schedule`, `appt`, `ask_cancel`, `m_home`), each with the page and the action that leads to it.
- **Capture data:** what state the data must be in (a busy day, a waiting patient, an unread message) and how you will get it.

Wait for "go".

## Step 2 - Capture

0. **Capture on a copy.** Copy the whole project to a capture folder and work there; the delivered project is never touched. On the copy, make the Production screens possible without a real server or provider (these are capture-only patches, listed here so you never invent your own):
   - `Local.Request()` returns `true` when there is no `HttpContext` (the preview server has none), so the first-sign-in box shows.
   - Write `data/initialized.txt` by hand before the first start, so the first Production start does not wipe the sample records you are about to photograph.
   - Payment or refund calls to the provider are simulated with a realistic id (`re_3Q…`, `pi_3Q…`), and the config carries a key that *looks* set (`sk_live_…CaptureOnly…`), so Settings shows "set" and the refund desk works. Nothing contacts the provider.
   - In the sample data, replace the test-payment wording with the real method name (`"Card (Stripe)"`), `pi_demo_`/`cs_demo_`/`re_demo_` ids with provider-shaped ids, and `"source": "demo"` with `"stripe"`, so no screenshot says demo.
   - For a reset-link or notification email, point `app.mail.server` at a local SMTP on port 25 (a 30-line Python socket server that answers 220/250/354 is enough) and read the mail it writes.
1. **Back up** `data/`, `appConfig/` and `temp/` of the capture copy too, so a step can be rerun on fresh data.
2. **Fill the data for the screenshots.** Start from the site's sample data (`data/`, see the website skill's initialize.md); it already has staff for each role and records in every status. If the site has none, write a small script that adds invented records to the copy in `data/`: staff for each role, customers or patients, bookings or orders around today with every status, a few website messages. Make today look like a working day: earlier visits done, one in progress, one waiting, the rest booked. If you capture at night or on a closed day, set the site's time zone in the copied data to one where it is now mid-afternoon on a working day (UTC+12, +13 or +14 cover most hours), so sessions are running and the dashboard is busy; put the real time zone back before you capture the Settings page. A site that moves its sample dates to today on the first run rewrites `data/` as soon as it starts, one more reason to restore from the backup.
3. Start the app on your computer and open `/AdminLogin`. Screenshot the first-sign-in box (`first_signin`), sign in with the password it shows, screenshot the *choose your own password* step (`first_choose`), and save a new password. Then sign in as a manager with a real-looking name, so the header and the activity log show a person, not `admin`.
4. Copy `${CLAUDE_SKILL_DIR}/scripts/capture.template.js` next to the site, rewrite the steps, and run it:

```bash
MANUAL_USER=<manager login> MANUAL_PASS=<their password> node capture.js http://localhost:5180 manual/raw
```

   - Desktop at 1440 × 900 with `deviceScaleFactor: 2`; phones at 390 × 844 with names starting `m_`.
   - Windows and dialogs: element screenshots (`part()`), taken with a tall viewport so nothing is cut.
   - Confirm dialogs: open them, screenshot, then step back or confirm.
   - Rerun one step with a third argument: `node capture.js <url> manual/raw schedule,users`. Steps that change data need the data reset first.
5. **Prove the delivered project is untouched**: `diff -rq <project> <capture copy>` lists only the capture-only patches and the records the capture added, all of them in the copy. Delete the copy when the manual is built.
6. Convert to JPEG (full screens 1100 px wide, windows half their pixel width up to 1100, phones 430):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/convert.py manual
```

Look at every image (a contact sheet helps). Recapture any with placeholder text, a toast in the way, a half-loaded list or a broken layout.

## Step 3 - Write

Start from `${CLAUDE_SKILL_DIR}/assets/body.template.html`. Write the manual in parts, `manual/src/body1.html`, `body2.html` ... (the first part opens `hm-app`, the last closes it and holds the `hm-zoom` element). To change colours, copy `assets/manual.css` to `manual/src/manual.css` and set `--accent`, `--accent-d`, `--ink`, `--bg`, `--note-bg` and `--note-line` from the site's palette.

| Element | Markup |
|---|---|
| Chapter | `<section class="hm-section" id="schedule" data-title="3. Day Schedule">` with `<h1 class="hm-h1">` |
| Topic (menu entry, search unit) | `<h2 id="changing-the-time">3.4 Changing the time</h2>`; every h2 needs an id |
| Screenshot | `<img loading="lazy" alt="..." src="{{img:schedule}}"/>`; window shots add `class="pad"` |
| Two or three phones | `<div class="hm-pair">` around the images |
| Caption | `<p class="hm-cap"><em>...</em></p>` |
| Tip / warning | `<div class="hm-note">` / `<div class="hm-warn">` |
| Table | `<div class="hm-tw"><table>` |
| Status | `<span class="hm-pill p-booked">` (also `p-conf`, `p-wait`, `p-occ`, `p-done`, `p-red`, `p-in`, `p-out`) |
| Cross-link | `<a href="#users" data-target="users" data-sub="rights">10.3</a>` |
| Keys, code, booking codes | `<kbd>Esc</kbd>`, `<code>/AdminLogin</code>`, `<span class="p-code">WC-7G3VCG</span>` |

**Diagrams:** inline SVG in `<div class="hm-diagram">`, `viewBox="0 0 1000 H"`, `width:100%`, the site's palette, text 10 px or larger, a unique id for every `marker` and `pattern`. Leave room for labels: band titles go where no arrow crosses them, button labels must fit inside their boxes, callout lines must not run through text. Draw the real screen (the sign-in card, the admin frame) simplified, not a generic box.

**Chapter content:** what the page is for, a screenshot, then one topic per task in the order people do them (find, open, change, confirm), each with numbered steps when there are steps, and the limits that apply (rights needed, what the server refuses). Installation & Setup holds the first sign-in (the box, choosing a password, the file in `appConfig/`, what to do when locked out), folder write rights, HTTPS, the 404 check for `data/` and `appConfig/`, backups, and redeploying without overwriting `data/`. Quick Answers is a two-column table of real front-desk questions.

## Step 4 - Build and check

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build.py manual "Willowmere Clinic"
node ${CLAUDE_SKILL_DIR}/scripts/check.js manual/Willowmere_Clinic_User_Manual.html manual/check
```

`build.py` embeds the JPEGs and reports missing and unused images; `check.js` fails on placeholder words (`demo`, `demo1234`, `sample`, `lorem`, `TODO` by default; add the site's own as the third argument; "sample" is allowed only where you write "invented" instead), broken cross-links, h2 without id, broken images, content wider than the page at 1440, 820 and 390, JavaScript errors, an empty search and a zoom that does not open. It also saves every diagram as a PNG: open each one and fix overlapping text, labels on lines and text outside boxes.

Then read the whole manual once more against the code: every number, button name and right.

## Step 5 - Deliver

Send the one HTML file. List, in a few lines, the site problems found while capturing and whether they were fixed. Confirm that the delivered project was not touched (`diff -r <project> <capture copy>` shows only the capture-only patches, all of them in the copy) and that its `data/`, `appConfig/` and `temp/` are as they were.

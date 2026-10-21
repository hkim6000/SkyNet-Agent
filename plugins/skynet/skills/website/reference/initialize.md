# Sample data and Initialize data

Read this when the site has a staff area. Every such site ships with sample records so the Demo looks like a working business, and with one way to wipe them when the owner goes live. Worked example (namespace `MySite`): [code/init/](code/init/) holds `Init.cs` and the additions to `AdminSettings`, `AdminLogin`, `Program.cs` and `Store`.

## Sample data

Write the sample records yourself, as JSON files in `data/`, after the pages are built and before verifying. They are part of the delivery.

- **Dates around the build day.** "Today" has records in every live status (one waiting, one in progress, one done and paid), a few days of history, and a few upcoming. Use the real date the site is built on; the owner replaces the data anyway.
- **Every status appears at least once** in every list the staff area has (new, sent, accepted, declined, expired; scheduled, on the way, done, cancelled; unpaid, overdue, paid, void; read and unread messages; refused rows in the activity log).
- **Staff for each role, no manager.** One account per role the rights table names (office, front desk, a few technicians or stylists linked to their own record with Own). All share the password `demo1234`, written in the README so visitors can try each role. There is no sample manager: the first-admin flow still makes the owner's manager on the first Production start.
- **Invented people and places** with `example.com` emails and 555 phone numbers. No reviews or testimonials unless the site's staff wrote them from feedback inside the sample flow.
- **Counters move.** If records carry running numbers (invoices, orders), set the next number in `site.json` past the sample ones.
- **The README** lists the sample files and says that Initialize data removes them.

Demo mode signs anyone in as the demo manager; a sample login name with its password signs in as that person, so the Own-only views can be shown.

## Initialize data

Going live must not carry the sample records, or anything testers added in Demo, into Production. `Core/Init.cs` does it once.

- **Automatic, once.** `Init.OnStart()` runs from `Program.cs` and from `AdminLogin.OnInitialized`. In Demo it returns at once. In Production it checks `data/initialized.txt`; if the file is missing it deletes every record file (`Records` in `Init.cs`: requests, orders, bookings, invoices, messages, reviews, the activity log and `staff.json`), the session file, `appConfig/initial-admin.txt` and uploaded customer files, writes the marker with the date and the count, and logs "initialize data" as `system`. The next sign-in page shows a new first password, as on a fresh install.
- **Never twice.** Later starts, and switching to Demo and back, do nothing while the marker exists. Real data entered in Production is never removed by the site.
- **Kept.** `site.json` (business details, prices, service area, Pages content), `media.json` and the media files, `application.cfg`.
- **Manual.** Settings shows **Initialize data** to managers, in Demo mode only. The confirm dialog needs the word `INITIALIZE` typed in capitals; the server checks the word, the Admin right and the mode again, logs the request, runs the same `Init.Run` without writing the marker (so the go-live run still happens), and signs everyone out. In Production the method refuses with a message.

### Before delivering

- Set `app.app.runmode | 1`, open `/AdminLogin`: the record files are gone, `data/initialized.txt` exists, the first-admin box shows, and the activity log holds one "initialize data" line by System. Add a record, open the page again: it stays. Switch to `0` and back to `1`: it stays.
- Back in Demo with the sample data restored: a non-manager does not see the button; the manager's dialog refuses `initialize` in lower case and accepts `INITIALIZE`; the toast says how many records went and the session ends.
- The README's "Going live" section explains both paths and the shared sample password.

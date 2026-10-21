# Customer accounts

Read this when customers sign in: students, members, patients, buyers with order history. Worked example (namespace `MySite`, a school with students): [code/accounts/](code/accounts/) holds `Mailer.cs`, the customer model and reset link, the `Join` page (gateway, sign-up, sign-in, forgot, reset), the Auth methods and the Account page windows.

Customers and staff are different things: separate records (`students.json`, not `staff.json`), separate sessions (`temp/students/sessions.json`, 14 days), a separate cookie (`xx_stu`) and a separate sign-in page. A staff account never signs in on the customer page and a customer never reaches `/AdminLogin`.

## The gateway

The header's **Sign in** opens one page (`Join`) with two cards:

- **Customers** (the site's word: Students, Members): tabs **Sign in** and **Create account**, with the sign-in form open first (`?mode=new` opens the other).
- **Staff and instructors**: three lines on who signs in here and a dark **Go to staff sign in** button to `/AdminLogin`, plus *No staff account? Ask your manager to add you.*

Every public footer also links to **Staff sign in**. `/AdminLogin` links back to *the student page*. Markup: [code/accounts/Join.gateway.html](code/accounts/Join.gateway.html).

## Sign-up

- Fields: name, email, **phone**, password twice. All required. The phone takes 7 to 15 digits with spaces, brackets, dots, dashes or a plus sign (`Ui.IsPhone`). One account per email; the email is the sign-in name and the customer cannot change it (staff can).
- Validation on the server, one error element per field (`xx-e-name`, `xx-e-phone`...). A duplicate email says *That email already has an account. Sign in instead.*
- On success the customer is signed in and sent to `?next=` (checked against `^[A-Za-z]+(\?[A-Za-z0-9=&%._-]*)?$` and never `Join` itself) or the account home.

## Sign-in

- Email and password. One message for every failure: *The email or password is not right.* After 6 wrong tries for one email in 5 minutes: *Too many tries. Wait a few minutes and try again.*
- In Demo the form is pre-filled with the first sample customer and a note lists the others with the shared password; in Production the fields are empty ([admin.md](admin.md#run-mode-demo-and-production)).
- **Forgot your password?** under the Sign in button opens the reset form on the same card.

## Password reset by email

`Mailer.cs` reads `app.mail.server`, `port`, `addr`, `id`, `password`, `title` and `credentials` from `application.cfg` and sends plain-text mail with `System.Net.Mail` (STARTTLS unless the port is 25). `Mailer.Ready` is false while the address or the password is still the placeholder.

1. **Forgot** takes an email. When mail is not set up it answers *Password reset by email is not set up on this site yet. Please contact us at <email> or <phone>...* and stops. Otherwise it always answers *If that email has an account, we have sent it a link to choose a new password. The link works for one hour.*, whether or not the account exists, so the page never tells a stranger which emails have accounts. The same 6-in-5-minutes pause applies per email.
2. If the account exists: a 16-byte random token; `data/resets.json` keeps its SHA-256 hash, the customer id, an expiry one hour ahead and `Used`; older links of the same customer are dropped. The email carries `<BaseUrl>/Join?reset=<token>` and says to ignore it if it was not them. The log line is *password reset link*, marked failed when the mail server refused.
3. `Join?reset=<token>` shows **Choose a new password** with the account's email, or *This link has expired or was already used. Ask for a new one below.* when the hash is unknown, used or past its hour.
4. **Reset** checks the token again, saves the new password (8 characters or more, typed twice), marks the link used, closes every session of the customer and signs them in. Log: *password reset*.

`resets.json` is one of the record files Initialize data removes.

## The account page

- **Edit profile**: name and phone, same checks as sign-up. The email is shown but not editable; the text says to write to the school to change it.
- **Change password**: current password, new password twice. Refuses a wrong current password, fewer than 8 characters, a mismatch and the same password again (*Choose a password different from the current one.*). On success the other sessions of the customer close and this one stays. Log: *change own password*, failed attempts too.
- Staff keep **Reset password** on the customer record (a new password shown once, all sessions closed) for the phone call that still happens.

## Before delivering

- Create an account without a phone: refused. With a phone: signed in, the phone shows in the staff list and record.
- Header **Sign in** shows the two cards; footer **Staff sign in** goes to `/AdminLogin`; `/AdminLogin` links back.
- Forgot with mail not set up: the contact message. With mail set up (a local SMTP on port 25 is enough for the test): an unknown email and a known email get the same message; the known one gets a mail with a link; the link opens the new-password form; a short password is refused; after saving, the old password is refused, the new one works, and the same link says it was used.
- Change password: wrong current, mismatch and success; another signed-in browser of the same customer is signed out, the one that changed it is not.
- The README's Going live section tells the owner to fill in `app.mail.*` and what happens until they do.

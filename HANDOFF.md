# ECSACONM Events — Session Handoff

> Quick-reference for the next development session. Production:
> **https://events.ecsaconm.org** · repo `main` branch.

Everything below is **committed and deployed** to production unless flagged
**IN PROGRESS** / **PENDING**. See `TEAM.md` (setup, deploy) and
`deployment.md` (incidents) for the standard process.

---

## What changed this session (commits)

| Commit | Change |
|---|---|
| `59e1ce6` | Badge PDF rewritten to match `BadgeCard.vue` exactly — every measurement derived from the 380px preview design mapped onto A5 (`PX = W/380`). |
| `02f5e6b` | Badge logos keep transparency (no more white boxes); fixed `deploy.sh` "dry-run" label bug. |
| `538daeb` | Event selectors use a valid `limit` (100) so `/events/?limit=200` stops 422ing. |
| `2f8ad6b` | Event participants search keeps focus (silent reloads); pagination uses the **filtered** total; "Extract Report" exports the full filtered set. |
| `6e7f2c9` | **Secretariat = paid** rule: `Registration.is_paid` hybrid (`paid OR role==secretariat`) used across events, registrations, abstracts, badges, users. Stored `paid` flag untouched. |
| `9afdae0` | Event visual report uses the **whole** event roster (fetches all pages), not the current 25-row page. |
| `fec120f` | **Secretariat** filter chip on the event participant list (+ `filter_counts.secretariat`). |
| `8e6bd01` | **Edit Participant** button/modal on `/user/:id` (title, name, phone, designation, organisation, country, role) via `PUT /registrations/{id}`. Backend now returns `registration_id`/`participation_role` on the user's events. |
| `fde76a4` | **Add Participant** `+` button on the event toolbar → `POST /events/{id}/participants` (finds/creates user + profile + registration; new accounts: password `Ecsaconm@2025`, role `User`). |
| `9ee12a9` | **Bulk badge export**: row checkboxes, `?ids=` subset, **4-up on A4** (each badge scaled A5→A6 with A5 proportions, cut guides), **preview modal** (BadgeCard grid), and export tracking via new `registration.badge_exported_at` (Alembic `e6f7a8b9c0d1`). Single badges stay one A5 page. |
| `9685250` | Badge selection can span **all pages** ("Select all N across pages", respects current filter/search). |
| `6efd158` | Scanned-QR page faster: `/events/scan` eager-loads in ~1 query and derives "today" in Python; confirm updates history locally (no 1.2s re-fetch). |
| `96612bc` | **Attendance confirmation is per-day**: one column per event day (start→end) with a checkbox per participant/day, day-level select-all, days-attended count, and export with one column per day. `create_attendance` accepts `attendance_date` (one record per registration per date). |
| `8a87d3e` | **Round profile photo** on badges (preview + PDF) when uploaded, between name and category bar; QR shrunk (default 96px). No photo → unchanged layout. |
| `ed65e05` | Photo enlarged to **5rem/80px**; badge layout compacted (header margins, name 24→22, category bar 38→32, QR floor 40px) so photo + content still fit A5. |
| `664f809` | **Search session persistence**: Registrations & Users lists write search/page/filters to the route query and restore them on mount — searching, opening a single view, and going back keeps the search. `SearchComponent` accepts a controlled `value` prop. |
| `df0dfb5` | **Removed the badge "ID #…" label** and enlarged the QR to fill its card: photo badges ~26mm, no-photo ~46mm (max). Preview QR mirrors the print (80px with photo, 120px default). |
| `56d5b80` | PDF profile photo **centre-cropped to fill the circle** (object-cover, like the preview); QR card padding reduced (~1.6mm) so the QR sits with a small margin — photo badges ~29mm. |
| `5f9fc02` | **Role-coloured badge category bars**: only the category bar changes per role — delegates keep navy, secretariat=green, media=amber, exhibitor=teal, usher=blue (others default to navy). Mirrored in the preview via `badgeCategoryGradient()`. Added **Media + Usher** to the `ParticipationRole` enum, admin/public role lists, Excel import map and display maps (migration `f1a2b3c4d5e6` extends the MySQL ENUM). |
| `a1ccaa4` | **Role dropdowns trimmed to the main five** (Delegate, Secretariat, Media, Exhibitor, Usher): Event "Add Participant" select + Registrations edit form. Legacy fee-based delegate categories (member_state/participant/other_africa/student) normalise to `delegate` on edit, and the public `/#/register/:id` form stores those categories as delegate (fees/labels unchanged). |
| `b2714b4` | **QR scan auto-records attendance** (no button): the status page POSTs on load and confirms "<name> has been marked for attendance on this date <date> and time <time> for Day N". `GET /events/scan/{id}` now returns `event.event_day` (1-based from start date). Added **Owen Mwandumbya** (`omwandumbya@ecsahc.org`) as Secretariat for the conference (user 734, registration 719). |
| `4ac56ff` | User page **"Edit Participant" popup role list trimmed** to the main five (Delegate, Secretariat, Media, Exhibitor, Usher), matching the add form; legacy delegate categories normalise to `delegate`. Created a **Finance role** (VIEW_EVENT, VIEW_REGISTRATIONS, VIEW_USER) assigned to **Diana Kaiza** (user 732, info@cosecsa.org) — she sees Events, Registrations, Users (+ Configurations/Sent Emails, both VIEW_USER-gated). She must re-login for the new permissions. |
| `e8c7cb6` | **Attendance Confirmation page stays blank until someone is scanned** — stats and the participant table only render once at least one attendance record exists; polls every 10s so QR scans appear automatically. |
| `7df8ec9` | **Fixed QR scan attendance** — the scan page sent `attendance_date` as a full ISO datetime, which the API rejects with a 422 (so scans never recorded attendance). Now sends a local `YYYY-MM-DD` date. |

## Production data changes

- **Secretariat (event 1)**: kept = Davis Kondamwali (`admission@cosecsa.org`,
  was `admin@ecsaconm.org`), Julius Tingai, Lemmy Mabuga, Dr Ntuli Kapologwe,
  Dr Mohammed Mohammed, Diana Kaiza (`info@cosecsa.org`, Administrative
  Officer), Samantha Mumbi (`samantha.mumbi@strathmore.edu`, Kenya). All others
  previously secretariat shifted to **delegate**. Ntuli/Mohammed were manually
  set to delegate by the user (regs 715/716) — do not "fix" back.
- **Retired duplicate user 60** → Joseph Sikora (`joseph.sikora@cosecsa.org`,
  soft-deleted) to free `admission@cosecsa.org` for the admin account.
- **Badge exports cleared** (all `badge_exported_at = NULL`).
- All kept secretariat profiles set to Tanzania; Samantha = Kenya.
- New accounts use default password **`Ecsaconm@2025`** and placeholder phone
  numbers — they should reset/update on first login.

## Deployment / DB

- Alembic head on production: **`e6f7a8b9c0d1`** (added `badge_exported_at`).
  Migration was applied to prod before the code deploy.
- Deploys use `deploy/deploy.sh api|web|migrate|status` — commit+push first.
  `web` needs no restart (Nginx). `api` restarts the `ecsaconm` service.

## Notes / gotchas for the next session

- `Registration.is_paid` is a read-time rule; the stored `paid` flag is still 0
  for most secretariat. Toggling paid on a secretariat row does nothing visible
  (rule overrides) — by design.
- The badge QR shrinks to ~14–18mm on dense badges (photo present) — expected
  trade-off the user accepted; close-range scanning works.
- `web/` (legacy frontend) is archived — only `web_vue/` is used.
- Pre-existing: user 60 originally had 3 `user_profile` rows (2 soft-deleted);
  unrelated. The `/events/?limit=200` 422 is fixed; keep selectors at limit ≤100.
- The attendance "Attended/Absent" stats mean "attended at least one day".
- Diana Kaiza has **no organisation** set (only designation) — user hasn't
  supplied one.

## PENDING / possible next steps (from user, not yet actioned)

- **Standalone check-in page**: if the scanned-QR page still feels slow on venue
  phones, build a tiny non-SPA page (the remaining cost is the app bundle).
- Confirm the attendance page "plain until confirmed" interpretation matches the
  user's expectation (currently plain checkboxes).
- If a bigger QR is wanted on dense badges, trim the header/name area instead.
# Deployment Notes

Operational log of deploy-time issues and how they were resolved — kept
alongside `TEAM.md` (which has the standard step-by-step deploy process).
Add an entry here whenever a deploy surfaces something future-you (or
another dev/agent) should know about.

---

## 2026-08-13 — Production server had uncommitted local edits, blocking `git pull`

**What happened**

While deploying the "Sent Emails" feature (commit `7bde421`), `git pull
origin main` on the production server failed to apply because the
server's working tree had **uncommitted local modifications** to files
that overlapped with the incoming changes:

```
modified:   api/models/models.py
modified:   api/routers/abstracts.py
modified:   api/routers/auth.py
modified:   api/routers/events.py
modified:   api/routers/presentation_templates.py
modified:   web/index.html
```

The server's `HEAD` was also 18 commits behind `origin/main`.

**Root cause**

These edits had been made **directly on the production server** (by Davis,
working with a separate agent session, editing files in
`/var/www/ecsaconm_events` over SSH) rather than through the normal
`local dev → commit → push → deploy` workflow described in `TEAM.md` §7.
The same fixes were later implemented independently in the normal dev
workflow and committed/pushed to GitHub (they correspond to the
"Scope presentation templates to oral or poster presenters", "Fix
template-type matching: use author-email presenter status", and
"Optimize banner uploads" commits already on `origin/main`). Because the
server copy was never reset to match, git saw two independent,
never-reconciled versions of the same lines — one sitting uncommitted on
the server, one already merged upstream — and refused to fast-forward.

**Resolution**

Diffed each file against `origin/main` to confirm the server-local
changes were a functional subset of what was already merged upstream (no
unique, undeployed production hotfix would be lost), then discarded them
and pulled cleanly:

```bash
git checkout -- api/models/models.py api/routers/abstracts.py \
  api/routers/events.py api/routers/auth.py \
  api/routers/presentation_templates.py web/index.html
git pull origin main
```

Also found (and left alone — untracked, harmless, don't block anything):
`api/events.py`, `api/events_space.py`, `api/routers/models.py` — stray
files on the server not tracked by git, likely leftovers from a manual
copy/backup. Worth cleaning up eventually but out of scope for this
deploy.

**Takeaway — don't edit the production server's working tree directly**

If a hotfix genuinely needs to go straight onto the server (e.g. an
outage), commit it there immediately and push it back to `origin/main`
(or cherry-pick it into the normal dev branch) **before the next
deploy**, so `git pull` never has to reconcile a diverged working tree.
Treat `/var/www/ecsaconm_events` on the server as a deploy target, not a
place to develop — same rule applies whether the edit is made by hand or
by an agent with SSH access.

---

## 2026-09-02 — `TEAM.md` was server-only; `deploy/deploy.sh` added; found another live hand-edit

While setting up scripted deploys, found that `TEAM.md` (the step-by-step deploy
guide `deployment.md` refers to at the top of this file) existed only on the
production server, untracked by git — a single point of failure. It's now
committed at the repo root, alongside a new `deploy/deploy.sh` (wraps §6's
rsync/ssh/systemctl steps; see `TEAM.md` §6 "Fast path") and `.vscode/tasks.json`
(gitignored, local-only — recreate it per checkout, or force-add it if the team
wants it shared) exposing those as VS Code Run Task entries.

Also found the same anti-pattern as the 2026-08-13 incident, on a smaller scale:
`api/routers/email_templates.py` had drifted from git (matched what later landed
in commits `7979000`/`498c521`/`2fe6d3b` — harmless, already reconciled) but
**`api/templates/registration_reminder_template.html` had been hand-edited on the
server** to repurpose the registration-reminder copy into an ad-hoc "abstract
deadline is today" blast (different subject framing, different CTA link), instead
of using the dedicated `abstract_submission_deadline_template.html` this repo
already has. The next `deploy/deploy.sh api` run will silently overwrite that
hand-edited file with git's version — which restores the *correct*
registration-reminder wording, but if that hijacked copy is still mid-use for an
active campaign, check with whoever's running it before deploying `api/`.

---

## 2026-09-02 — Outage: migration never ran, `alembic upgrade head` was silently broken

Ran `ecsaconm-deploy api` + `web` to ship the abstract-submission-open feature
(new `event.abstract_submission_open` column) without running `migrate` first.
Every `Event` query started throwing `1054 Unknown column
'event.abstract_submission_open'` — a hard 500 on `/events/` and anything that
touches it, i.e. most of the site. Live for a few minutes before caught.

Root cause, two layers:

1. **Forgot the migration step.** `deploy.sh`/`server-deploy.sh api` and `web`
   don't run `migrate` automatically — has to be called separately, on purpose
   (a migration is a schema change, riskier to bundle silently into every
   deploy). Should have run `migrate` first.
2. **`migrate` wouldn't have worked anyway.** `alembic.ini`'s `sqlalchemy.url`
   is a placeholder (`root:root@localhost` — never real credentials, since
   `alembic.ini` is committed to git) and `alembic/env.py`'s
   `run_migrations_online()` built its engine from that placeholder instead of
   the app's real one, which it already imported and then never used. Alembic
   had apparently never successfully connected to *this* database — the
   `alembic_version` table being at a real revision suggests it was applied
   against a local dev DB and hand-applied to prod separately (see the
   `presentation_template.presentation_type` commit: "applied directly to
   prod"). `alembic` also wasn't in `requirements.txt`, so it wasn't even
   installed in the server's venv until this incident.

**Fix**: `env.py` now points `run_migrations_online()` at `core.database.engine`
(the app's real, working engine) instead of building one from `alembic.ini`.
`alembic` (and its `Mako` dependency) added to `requirements.txt`. The missing
column was applied directly via `sudo mysql` to restore service immediately,
and `alembic_version` updated to match by hand — `alembic upgrade head` should
now be a genuine no-op for it, and should actually work for future migrations.

**Takeaway — always run `migrate` before/with `api` when a change touches
`api/models/models.py`**, and don't assume `alembic upgrade head` works just
because it's the documented command; this incident is the first time anyone
actually depended on it running successfully against production.

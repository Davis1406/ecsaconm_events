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

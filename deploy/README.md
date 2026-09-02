# Deploy scripts

Two ways to deploy, same underlying steps (TEAM.md §6/§7) — pick whichever matches
where you're sitting.

## `deploy.sh` — run from your own machine

Pushes your local working tree to the server (`rsync`, or plain `tar`-over-`ssh` if
`rsync` isn't installed) and restarts the service remotely.

```bash
deploy/deploy.sh api --dry-run   # preview
deploy/deploy.sh api             # sync api/, restart the ecsaconm service
deploy/deploy.sh web             # npm run build locally, then sync dist/
deploy/deploy.sh migrate         # alembic upgrade head on the server
deploy/deploy.sh status          # systemd status + recent logs
deploy/deploy.sh logs            # follow live API logs
```

Refuses to run against a dirty local working tree unless you pass `--allow-dirty`
(it reads straight off disk, so commit and push first — same as any deploy).

## `server-deploy.sh` — run *on* the server, via SSH

`git pull`s the server's own checkout instead of pushing to it, then builds/restarts
in place. Only works because the server's checkout is kept clean — never edit files
under `/var/www/ecsaconm_events` directly (see `deployment.md` for what happens when
that rule breaks).

**One-time install**, on the server:

```bash
sudo ln -sf /var/www/ecsaconm_events/deploy/server-deploy.sh /usr/local/bin/ecsaconm-deploy
sudo chmod +x /var/www/ecsaconm_events/deploy/server-deploy.sh
```

After that, from anywhere on the box:

```bash
ecsaconm-deploy api       # git pull, restart the ecsaconm service
ecsaconm-deploy web       # git pull, npm install (if needed), npm run build
ecsaconm-deploy all       # both of the above
ecsaconm-deploy migrate   # alembic upgrade head
ecsaconm-deploy status    # systemd status + recent logs
ecsaconm-deploy logs      # follow live API logs
```

Refuses to pull if the checkout has uncommitted changes, for the same reason.

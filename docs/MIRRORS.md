# Repository mirrors

Promethea's canonical home is on GitHub. For long-term redundancy and
platform-independence, every push to `main` is auto-mirrored to:

| Host | URL | Role |
|------|-----|------|
| GitHub | https://github.com/KhaiB10/promethea | Canonical (PRs, issues, CI, releases) |
| GitLab | https://gitlab.com/KhaiB10/promethea | Read-only mirror |
| Codeberg | https://codeberg.org/KhaiB10/promethea | Read-only mirror |

The mirror workflow ([.github/workflows/mirror.yml](../.github/workflows/mirror.yml))
runs on every push to `main`, on manual dispatch, and on a nightly cron
(09:00 UTC) as a safety net.

## One-time setup (owner only)

1. **Create empty repos** under your username on:
   - https://gitlab.com/projects/new (visibility: public)
   - https://codeberg.org/repo/create (visibility: public)
2. **Generate write-scoped tokens**:
   - GitLab: <https://gitlab.com/-/user_settings/personal_access_tokens>,
     scope `write_repository`
   - Codeberg: <https://codeberg.org/user/settings/applications>,
     scope `write:repository`
3. **Add tokens as repo secrets** at
   <https://github.com/KhaiB10/promethea/settings/secrets/actions>:
   - `GITLAB_MIRROR_TOKEN`
   - `CODEBERG_MIRROR_TOKEN`

The workflow skips (without failing) any mirror whose secret is unset,
so you can enable the two hosts independently.

## Mirror policy

- Mirrors are **push-only** from GitHub. Do not commit directly to GitLab
  or Codeberg — pushes from this workflow use `--force`, and any
  out-of-band changes there will be overwritten.
- Tags (including release tags like `v0.2.0`) are mirrored.
- The default branch (`main`) is mirrored; other branches are not.
- Issues, PRs, and CI runs remain GitHub-only by design.

## Cite-mirroring

For citations, prefer the GitHub URL or the Zenodo DOI (once minted).
The GitLab and Codeberg mirrors exist for code recoverability, not as
primary references.

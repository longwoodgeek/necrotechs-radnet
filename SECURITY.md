# Public hailing frequency — deployment guide (2026-11-09)

**Verified destination:** https://github.com/GerryBM/necrotechs-radnet

GitHub confirms the repository is **public** and **empty**. The GitHub connection currently available to ChatGPT belongs to `longwoodgeek` and has **read-only** access to `GerryBM/necrotechs-radnet`. Nothing has been pushed to the public repository. **Do not make the private `longwoodgeek/sentinellink` repository public or copy its git history.**

## Publish using the GitHub website

1. On a Mac, unzip `NecroTechs_RadNet_Public_Launch_Kit.zip`.
2. Open `https://github.com/GerryBM/necrotechs-radnet` while signed into the **GerryBM** GitHub account.
3. Select **uploading an existing file** on the empty repo page (or **Add file → Upload files**).
4. Upload the **contents inside** the `necrotechs-radnet` folder, not the wrapping folder and not the outer ZIP. Preserve `docs/` paths. GitHub's web upload supports dragging folders in a desktop browser; verify the staged file paths begin at `README.md`, `LICENSE`, `docs/`, etc., and *not* `necrotechs-radnet/README.md`.
5. Inspect the staging list and file previews; confirm there are no secret files, images, personal IDs, raw host configurations or disk images. Commit with `Initial public RadNet documentation`.
6. Check README links, branch visibility `Public`, and the signed-out URL.

## Alternative: publish with Git on the Mac

Requires Git installed and an account with push rights to `GerryBM/necrotechs-radnet`. In the directory where the launch ZIP was downloaded:

```bash
unzip NecroTechs_RadNet_Public_Launch_Kit.zip -d radnet-public-staging
git clone https://github.com/GerryBM/necrotechs-radnet.git
cp -R radnet-public-staging/necrotechs-radnet/. necrotechs-radnet/
cd necrotechs-radnet
git status
git add README.md LICENSE .gitignore CONTRIBUTING.md SECURITY.md docs
git diff --cached --stat
git diff --cached --check
git commit -m 'Initial public RadNet documentation'
git push -u origin main
```

If Git rejects authentication, GitHub may require signing in, an authorized credential manager, or personal access token. **Don't paste any access token into ChatGPT.**

## Permit ChatGPT to push future changes

Because the currently connected GitHub identity is `longwoodgeek`, `GerryBM` can invite `longwoodgeek` as a collaborator with write permission, and the recipient must accept. If the GitHub app only has access to selected repositories, the new repository may additionally need to be authorized in the app's GitHub installation settings. Alternatively reconnect the GitHub integration under the account that owns this repository. All permission/connection changes require user action.

## Status and safety

- The original private repository `longwoodgeek/sentinellink` stays private.
- First public launch is **documentation only**. The experimental LinkProbe prototype is *not* published as validated firmware or a tested release.
- GNSS is proposed and SD card ext4 repair is pending. 100% rescued means the raw bytes were read successfully, not that the filesystem is fixed.
- Claims about field ranges are explicitly estimates and operator-reported, not official radio certification.
#!/usr/bin/env bash
# Run this on the Digital Ocean droplet as root:
#   ssh root@147.182.191.226 'bash -s' < deploy-setup.sh

set -euo pipefail

REPO="/var/repo/free-state-party.git"
WEBROOT="/var/www/freestate.party"

echo "==> Creating bare repo"
mkdir -p "$REPO"
git init --bare "$REPO"

echo "==> Writing post-receive hook"
cat > "$REPO/hooks/post-receive" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail

WEBROOT="/var/www/freestate.party"
TMPDIR=$(mktemp -d)

# Check out the pushed code
git --work-tree="$TMPDIR" checkout -f main

# Sync site/ contents to web root
# Preserve video/ (not in git, uploaded separately)
rsync -a --delete --exclude="video/" "$TMPDIR/site/" "$WEBROOT/"

rm -rf "$TMPDIR"
echo "==> Deployed to $WEBROOT"
HOOK

chmod +x "$REPO/hooks/post-receive"

echo "==> Done! Add this remote locally:"
echo "    git remote add production root@147.182.191.226:/var/repo/free-state-party.git"
echo "    git push production main"

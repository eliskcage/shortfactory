#!/bin/bash
# SHORTFACTORY CRITICAL FILE BACKUP SCRIPT
# Run on server: bash /var/www/vhosts/shortfactory.shop/httpdocs/backup-critical.sh
# Creates timestamped snapshots of all critical files in /backups/

WEBROOT="/var/www/vhosts/shortfactory.shop/httpdocs"
BACKUP_DIR="$WEBROOT/backups/$(date +%Y-%m-%d_%H%M)"
mkdir -p "$BACKUP_DIR"

CRITICAL_FILES=(
  "index.php"
  "soul-sphere.html"
  "index2.php"
  "index3.php"
  "nvidia.html"
  "soul-viewer.html"
  "api/soul-complete.php"
  ".htaccess"
  "join.html"
  "dan-soul.html"
  "alive/app.html"
  "alive/studio/index.html"
)

echo "=== SHORTFACTORY BACKUP === $(date)"
echo "Destination: $BACKUP_DIR"
echo ""

for f in "${CRITICAL_FILES[@]}"; do
  src="$WEBROOT/$f"
  if [ -f "$src" ]; then
    dest="$BACKUP_DIR/$(echo $f | tr '/' '_')"
    cp "$src" "$dest"
    lines=$(wc -l < "$src")
    size=$(stat -c%s "$src" 2>/dev/null || stat -f%z "$src" 2>/dev/null)
    echo "OK: $f ($lines lines, $size bytes)"
  else
    echo "MISSING: $f — FILE NOT FOUND"
  fi
done

# Keep only last 10 backup folders to save disk
cd "$WEBROOT/backups"
ls -dt */ 2>/dev/null | tail -n +11 | xargs rm -rf 2>/dev/null

echo ""
echo "=== BACKUP COMPLETE === Kept last 10 snapshots"

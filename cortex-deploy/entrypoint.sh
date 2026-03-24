#!/bin/bash
set -e

DATA_DIR="/app/data"
SRC_DIR="/app/src"

# Create hemisphere dirs on persistent volume if missing
mkdir -p "$DATA_DIR/left" "$DATA_DIR/right" "$DATA_DIR/cortex"

# Symlink volume dirs into src so online_server.py finds them
for hemi in left right cortex; do
  if [ ! -L "$SRC_DIR/$hemi" ]; then
    ln -s "$DATA_DIR/$hemi" "$SRC_DIR/$hemi"
    echo "[entrypoint] linked $SRC_DIR/$hemi -> $DATA_DIR/$hemi"
  fi
done

echo "[entrypoint] starting Cortex Brain on port ${PORT:-8643}"
exec python src/online_server.py

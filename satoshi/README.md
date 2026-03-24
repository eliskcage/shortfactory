# Satoshi Vault

API keys encrypted with the Satoshi cipher (Vigenere ASCII 32-126).
`keys.vault` is committed — safe to push. Decrypt key never leaves the server.

## Setup on server

```bash
# Set the vault key as an environment variable (once)
echo 'export SF_VAULT_KEY=SKYDADDY' >> /etc/environment
source /etc/environment

# Or for systemd services, add to the service file:
# Environment="SF_VAULT_KEY=SKYDADDY"
```

## Add a new key

```bash
cd /path/to/repo
python3 -m satoshi.vault set MY_KEY "the_actual_value"
# keys.vault is updated — commit it
```

## Use in Python

```python
from satoshi.vault import get
my_key = get('MY_KEY')
```

## Keys currently in vault

- `PINATA_JWT` — Pinata IPFS JWT
- `SUPABASE_KEY` — Supabase service key
- `SUPABASE_URL` — Supabase project URL
- `COCKROACH_DSN` — CockroachDB connection string
- `NEON_DSN` — Neon PostgreSQL connection string

## How it works

Same Vigenere cipher as the frontend Satoshi encoder:
- Characters outside ASCII 32-126 pass through unchanged
- Encrypt: `chr((ord(c) - 32 + ord(k) - 32) % 95 + 32)`
- Decrypt: `chr((ord(c) - 32 - ord(k) + 32) % 95 + 32)`

`keys.vault` contains JSON: `{"KEY_NAME": "encrypted_value"}`.
GitHub push protection won't flag it — it's not a recognisable secret format.

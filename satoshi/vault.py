"""
Satoshi Vault — API key encryption/decryption
Vigenere cipher over ASCII 32-126, same algorithm as the frontend.
Decrypt key comes from env var SF_VAULT_KEY (never committed).
Usage:
    from satoshi.vault import get
    xai_key = get('XAI_KEY')
"""

import os
import json
import pathlib

_VAULT_FILE = pathlib.Path(__file__).parent / 'keys.vault'
_KEY_ENV     = 'SF_VAULT_KEY'
_cache       = {}


def _satoshi(text: str, key: str, encode: bool) -> str:
    result = []
    ki = 0
    for c in text:
        o = ord(c)
        if 32 <= o <= 126:
            k = ord(key[ki % len(key)]) - 32
            if encode:
                result.append(chr((o - 32 + k) % 95 + 32))
            else:
                result.append(chr((o - 32 - k) % 95 + 32))
            ki += 1
        else:
            result.append(c)
    return ''.join(result)


def encode(text: str, key: str) -> str:
    return _satoshi(text, key, True)


def decode(text: str, key: str) -> str:
    return _satoshi(text, key, False)


def _vault_key() -> str:
    k = os.environ.get(_KEY_ENV)
    if not k:
        raise RuntimeError(
            f'SF_VAULT_KEY env var not set. '
            f'Run: export SF_VAULT_KEY=your_key'
        )
    return k


def _load() -> dict:
    if not _VAULT_FILE.exists():
        return {}
    return json.loads(_VAULT_FILE.read_text())


def get(name: str) -> str:
    """Retrieve and decrypt a key from the vault."""
    if name in _cache:
        return _cache[name]
    vault = _load()
    if name not in vault:
        raise KeyError(f'Key "{name}" not in vault. Run: python -m satoshi.vault set {name} <value>')
    decrypted = decode(vault[name], _vault_key())
    _cache[name] = decrypted
    return decrypted


def set_key(name: str, value: str):
    """Encrypt and store a key in the vault."""
    vault = _load()
    vault[name] = encode(value, _vault_key())
    _VAULT_FILE.write_text(json.dumps(vault, indent=2))
    print(f'OK: {name} stored in vault')


def list_keys():
    vault = _load()
    if not vault:
        print('Vault is empty.')
        return
    print('Keys in vault (encrypted):')
    for k, v in vault.items():
        print(f'  {k}: {v[:20]}...')


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if not args or args[0] == 'list':
        list_keys()
    elif args[0] == 'set' and len(args) == 3:
        set_key(args[1], args[2])
    elif args[0] == 'get' and len(args) == 2:
        print(get(args[1]))
    elif args[0] == 'encode' and len(args) == 3:
        print(encode(args[1], args[2]))
    else:
        print('Usage:')
        print('  python -m satoshi.vault list')
        print('  python -m satoshi.vault set KEY_NAME value')
        print('  python -m satoshi.vault get KEY_NAME')

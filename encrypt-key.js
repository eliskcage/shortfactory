/**
 * Satoshi Cipher key encryptor — run once to generate .api_key ciphertext
 * Usage: node encrypt-key.js <YOUR_XAI_KEY> <PASSPHRASE>
 * Output: ciphertext to paste into alive/studio/.api_key
 */

function satoshiEncrypt(plaintext, passphrase) {
  var result = '';
  var p = passphrase.toUpperCase();
  for (var i = 0; i < plaintext.length; i++) {
    var c = plaintext.charCodeAt(i);
    var k = p.charCodeAt(i % p.length);
    result += String.fromCharCode(((c - 32) + (k - 32)) % 95 + 32);
  }
  return result;
}

function satoshiDecrypt(ciphertext, passphrase) {
  var result = '';
  var p = passphrase.toUpperCase();
  for (var i = 0; i < ciphertext.length; i++) {
    var c = ciphertext.charCodeAt(i);
    var k = p.charCodeAt(i % p.length);
    result += String.fromCharCode(((c - 32) - (k - 32) + 95) % 95 + 32);
  }
  return result;
}

var key  = process.argv[2];
var pass = process.argv[3];

if (!key || !pass) {
  console.log('Usage: node encrypt-key.js <XAI_API_KEY> <PASSPHRASE>');
  console.log('Example: node encrypt-key.js xai-abc123... KILLIAN');
  process.exit(1);
}

var cipher = satoshiEncrypt(key, pass);
var verify = satoshiDecrypt(cipher, pass);

console.log('\n── SATOSHI ENCRYPTED KEY ──────────────────────────');
console.log(cipher);
console.log('\n── VERIFICATION (should match your original key) ──');
console.log(verify === key ? '✓ Matches — safe to use' : '✗ MISMATCH — do not use');
console.log('\n── NEXT STEPS ──────────────────────────────────────');
console.log('1. Copy the ciphertext above');
console.log('2. SSH to medium server and run:');
console.log('   mkdir -p /var/www/vhosts/shortfactory.shop/httpdocs/alive/studio');
console.log('   echo "PASTE_CIPHERTEXT_HERE" > /var/www/vhosts/shortfactory.shop/httpdocs/alive/studio/.api_key');
console.log('3. Add passphrase to systemd service:');
console.log('   Edit /etc/systemd/system/card-server.service');
console.log('   Add under [Service]: Environment=SF_KEY_PASS=' + pass);
console.log('4. Reload and restart:');
console.log('   systemctl daemon-reload && systemctl restart card-server');

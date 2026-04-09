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

var ct = "e\\Yq#7(BS]iVWDQY\u2019t!luDJY|y0iswiY$})kseq-\n(4?D%7*;HAL*5D(;BKM*\u2019D3IKYYe0)DN<1Y2#(-CB1Y(#3D@=:>D6-*YD>I,4&2Y:>I2A9-?S-H89*7g";

// Try stripping the newline — treat as one continuous string
ct = ct.replace(/\n/g, '');

console.log('SKYDADDY:', satoshiDecrypt(ct, 'SKYDADDY'));
console.log('KILLIAN:', satoshiDecrypt(ct, 'KILLIAN'));
console.log('Length:', ct.length);
console.log('Raw chars:', ct.split('').map(function(c){ return c.charCodeAt(0); }).join(','));

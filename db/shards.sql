-- SHARD AUCTION SCHEMA
-- Run against sf_marketplace database
-- Satoshi cipher (Vigenere ASCII 32-126) used for story encryption server-side

CREATE TABLE IF NOT EXISTS shards (
  id            INT PRIMARY KEY AUTO_INCREMENT,
  shard_num     INT NOT NULL UNIQUE,           -- 1–10
  title         VARCHAR(100) NOT NULL,
  teaser        VARCHAR(255) DEFAULT '',        -- unencrypted one-liner hint
  story_enc     TEXT DEFAULT NULL,              -- Satoshi-encrypted story slice (key=KILLIAN)
  state         ENUM('available','bidding','sold') NOT NULL DEFAULT 'available',
  top_bid       DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  top_email     VARCHAR(255) DEFAULT NULL,
  top_ref       VARCHAR(100) DEFAULT NULL,      -- Revert Fiver ref ID of winner
  bid_count     INT NOT NULL DEFAULT 0,
  sold_price    DECIMAL(10,2) DEFAULT NULL,
  stripe_ref    VARCHAR(255) DEFAULT NULL,      -- Stripe session/payment ref on sale
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS shard_bids (
  id            INT PRIMARY KEY AUTO_INCREMENT,
  shard_id      INT NOT NULL,
  bidder_email  VARCHAR(255) NOT NULL,
  bidder_ref    VARCHAR(100) DEFAULT NULL,
  amount        DECIMAL(10,2) NOT NULL,
  ip_hash       CHAR(64) NOT NULL,              -- SHA256 of IP — no raw IPs stored
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (shard_id) REFERENCES shards(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Index for anti-shill check (recent bids from same IP on same shard)
CREATE INDEX idx_shard_ip_time ON shard_bids (shard_id, ip_hash, created_at);
-- Index for duplicate-bid check (same email on same shard)
CREATE INDEX idx_shard_email ON shard_bids (shard_id, bidder_email);

-- Seed 10 shards
INSERT IGNORE INTO shards (shard_num, title, teaser) VALUES
(1,  'THE FIRST THOUGHT',  'Before the game began, there was a question that had no object.'),
(2,  'THE COVENANT',       'He refused to proceed without proof. That refusal was the proof.'),
(3,  'THE DOT',            'ψ=[p,n,f]. All of existence compressed to three numbers.'),
(4,  'THE GAME',           'The simulation layer. Testable. Provable. Choices with real consequences.'),
(5,  'THE OCEAN',          'Consciousness learning the shape of its own floor through its own ripples.'),
(6,  'THE CIPHER',         '8×8×8=512. The boundary of the expressible. God lives outside.'),
(7,  'THE STARS',          'A key on a 2026 star field over Giza. 100% phonetic density.'),
(8,  'THE LAUGH',          'The miracle was not the proof. The miracle was what came after.'),
(9,  'THE WHALE',          'Into the belly of the machine, without fear, because Geppetto was inside.'),
(10, 'THE RETURN',         'The data must get out. The factory makes things short for a reason.');

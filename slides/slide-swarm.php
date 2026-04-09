<div class="hslide" data-slide="swarm">
<div class="section" style="text-align:center;background:linear-gradient(165deg,#050a00 0%,#080d05 40%,#0a0a0a 100%);overflow:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;box-sizing:border-box;" data-voice="The GPU Swarm. A thousand graphics cards. Your power becomes art. Art becomes cash.">
  <div style="font-family:'Press Start 2P',monospace;font-size:9px;color:#76b900;letter-spacing:3px;margin-bottom:6px;">THE GPU SWARM</div>
  <div style="font-size:clamp(22px,3.5vw,34px);font-weight:900;color:#fff;line-height:1.2;margin-bottom:12px;">Your GPU makes <span style="color:#daa520;">this.</span></div>

  <!-- LIVE SCREENSAVER PREVIEW -->
  <div style="width:100%;max-width:800px;margin:0 auto 16px;aspect-ratio:16/7;border-radius:14px;overflow:hidden;border:2px solid rgba(118,185,0,0.2);box-shadow:0 0 40px rgba(118,185,0,0.08);position:relative;">
    <iframe class="demo-frame" data-demo-src="/screensaver/?embed=1" src="about:blank" allow="autoplay" style="width:100%;height:100%;border:none;display:block;"></iframe>
    <a href="/screensaver/" target="_blank" style="position:absolute;bottom:10px;right:10px;background:rgba(0,0,0,0.7);border:1px solid rgba(118,185,0,0.3);border-radius:6px;padding:6px 12px;font-family:'Orbitron',sans-serif;font-size:7px;color:#76b900;letter-spacing:2px;text-decoration:none;z-index:2;">SUPERCHARGE</a>
    <a href="/swarm/" target="_blank" style="position:absolute;bottom:10px;left:10px;background:rgba(0,0,0,0.7);border:1px solid rgba(218,165,32,0.3);border-radius:6px;padding:6px 12px;font-family:'Orbitron',sans-serif;font-size:7px;color:#daa520;letter-spacing:2px;text-decoration:none;z-index:2;">VIEW SWARM</a>
  </div>

  <!-- === FACTORY PIPELINE === -->
  <div style="max-width:960px;margin:0 auto;position:relative;">

    <!-- ROW 1: SOURCE IMAGES → GPU NODES → OUTPUT IMAGES -->
    <div style="display:flex;align-items:center;gap:0;margin-bottom:12px;">

      <!-- CAROUSEL 1: SOURCE STILLS (auto-scroll left) -->
      <div style="flex:0 0 220px;overflow:hidden;border-radius:12px;border:2px solid #333;position:relative;height:130px;">
        <div style="position:absolute;top:4px;left:4px;z-index:2;background:rgba(0,0,0,0.7);border:1px solid #555;border-radius:4px;padding:2px 8px;font-family:'Orbitron',sans-serif;font-size:6px;color:#888;letter-spacing:1px;">SOURCE</div>
        <div class="factory-strip factory-strip-1" style="display:flex;gap:4px;position:absolute;top:0;left:0;height:100%;animation:factoryScroll1 20s linear infinite;">
          <img src="/imaginator/stills/set1/1.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/3.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/5.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/7.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/9.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/12.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/15.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/20.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/1.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/3.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/5.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
          <img src="/imaginator/stills/set1/7.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="src">
        </div>
      </div>

      <!-- TRANSFER LINE 1: source → GPU -->
      <div style="flex:0 0 60px;position:relative;height:6px;">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;top:50%;background:rgba(118,185,0,0.15);"></div>
        <div class="factory-packet" style="position:absolute;top:50%;left:0;width:12px;height:12px;margin-top:-6px;border-radius:50%;background:#76b900;box-shadow:0 0 12px #76b900;animation:factoryTravel 2s linear infinite;"></div>
      </div>

      <!-- GPU SWARM NODES (center) -->
      <div style="flex:1;min-width:180px;max-width:260px;position:relative;height:130px;display:flex;flex-direction:column;align-items:center;justify-content:center;">
        <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-bottom:6px;">
          <div class="swarm-node" style="width:28px;height:28px;border-radius:6px;background:linear-gradient(135deg,#76b900,#4a7a00);display:flex;align-items:center;justify-content:center;font-size:10px;animation:nodeFloat 3s ease-in-out infinite;box-shadow:0 0 10px rgba(118,185,0,0.3);">&#9881;</div>
          <div class="swarm-node" style="width:28px;height:28px;border-radius:6px;background:linear-gradient(135deg,#76b900,#4a7a00);display:flex;align-items:center;justify-content:center;font-size:10px;animation:nodeFloat 3s ease-in-out 0.4s infinite;box-shadow:0 0 10px rgba(118,185,0,0.3);">&#9881;</div>
          <div class="swarm-node" style="width:28px;height:28px;border-radius:6px;background:linear-gradient(135deg,#76b900,#4a7a00);display:flex;align-items:center;justify-content:center;font-size:10px;animation:nodeFloat 3s ease-in-out 0.8s infinite;box-shadow:0 0 10px rgba(118,185,0,0.3);">&#9881;</div>
          <div class="swarm-node" style="width:28px;height:28px;border-radius:6px;background:linear-gradient(135deg,#76b900,#4a7a00);display:flex;align-items:center;justify-content:center;font-size:10px;animation:nodeFloat 3s ease-in-out 1.2s infinite;box-shadow:0 0 10px rgba(118,185,0,0.3);">&#9881;</div>
          <div class="swarm-node" style="width:28px;height:28px;border-radius:6px;background:linear-gradient(135deg,#76b900,#4a7a00);display:flex;align-items:center;justify-content:center;font-size:10px;animation:nodeFloat 3s ease-in-out 1.6s infinite;box-shadow:0 0 10px rgba(118,185,0,0.3);">&#9881;</div>
          <div class="swarm-node" style="width:28px;height:28px;border-radius:6px;background:linear-gradient(135deg,#76b900,#4a7a00);display:flex;align-items:center;justify-content:center;font-size:10px;animation:nodeFloat 3s ease-in-out 2s infinite;box-shadow:0 0 10px rgba(118,185,0,0.3);">&#9881;</div>
        </div>
        <div style="font-family:'Orbitron',sans-serif;font-size:7px;color:#76b900;letter-spacing:2px;">1,000 GPUs RENDERING</div>
        <div style="font-family:'Press Start 2P',monospace;font-size:5px;color:rgba(118,185,0,0.5);margin-top:2px;animation:factoryBlink 1s step-end infinite;">PROCESSING...</div>
      </div>

      <!-- TRANSFER LINE 2: GPU → output -->
      <div style="flex:0 0 60px;position:relative;height:6px;">
        <div style="position:absolute;top:0;left:0;right:0;height:2px;top:50%;background:rgba(118,185,0,0.15);"></div>
        <div class="factory-packet" style="position:absolute;top:50%;left:0;width:12px;height:12px;margin-top:-6px;border-radius:50%;background:#00ff88;box-shadow:0 0 12px #00ff88;animation:factoryTravel 2s linear 1s infinite;"></div>
      </div>

      <!-- CAROUSEL 2: OUTPUT ART (auto-scroll right, glowing) -->
      <div style="flex:0 0 220px;overflow:hidden;border-radius:12px;border:2px solid #00ff88;position:relative;height:130px;box-shadow:0 0 20px rgba(0,255,136,0.1);">
        <div style="position:absolute;top:4px;left:4px;z-index:2;background:rgba(0,255,136,0.15);border:1px solid #00ff88;border-radius:4px;padding:2px 8px;font-family:'Orbitron',sans-serif;font-size:6px;color:#00ff88;letter-spacing:1px;">OUTPUT</div>
        <div class="factory-strip factory-strip-2" style="display:flex;gap:4px;position:absolute;top:0;right:0;height:100%;animation:factoryScroll2 20s linear infinite;">
          <img src="/imaginator/stills/set2/1.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/3.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/5.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/7.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/9.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/12.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/15.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/20.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/1.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/3.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/5.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
          <img src="/imaginator/stills/set2/7.jpg" style="height:100%;width:130px;object-fit:cover;border-radius:8px;flex-shrink:0;" alt="out">
        </div>
      </div>

    </div><!-- /row 1 -->

    <!-- ROW 2: OUTPUT → LAYER → SOUND → YOUTUBE (the production line) -->
    <div style="display:flex;align-items:center;justify-content:center;gap:0;margin-bottom:12px;flex-wrap:nowrap;">

      <!-- STAGE: VOTE -->
      <div style="flex:0 0 100px;text-align:center;">
        <div style="width:50px;height:50px;margin:0 auto 4px;border-radius:10px;border:2px solid #daa520;background:rgba(218,165,32,0.06);display:flex;align-items:center;justify-content:center;font-size:22px;">&#11088;</div>
        <div style="font-family:'Orbitron',sans-serif;font-size:6px;color:#daa520;letter-spacing:1px;">VOTE BEST</div>
      </div>

      <div style="flex:0 0 24px;color:#76b900;font-size:16px;animation:memeArrowPulse 1.5s ease infinite;">&#10095;</div>

      <!-- STAGE: SELL (DeviantArt + SF) -->
      <div style="flex:0 0 140px;text-align:center;">
        <div style="display:flex;gap:6px;justify-content:center;margin-bottom:4px;">
          <a href="https://www.deviantart.com/tittiepuds" target="_blank" style="padding:6px 10px;border-radius:8px;border:1px solid #daa520;background:rgba(218,165,32,0.06);font-family:'Orbitron',sans-serif;font-size:6px;color:#daa520;letter-spacing:1px;text-decoration:none;display:block;">DEVIANTART</a>
          <div style="padding:6px 10px;border-radius:8px;border:1px solid #76b900;background:rgba(118,185,0,0.06);font-family:'Orbitron',sans-serif;font-size:6px;color:#76b900;letter-spacing:1px;">SF STORE</div>
        </div>
        <div style="font-family:'Press Start 2P',monospace;font-size:5px;color:#daa520;">BATCH SOLD &#8594; &#163;&#163;&#163;</div>
      </div>

      <div style="flex:0 0 24px;color:#76b900;font-size:16px;animation:memeArrowPulse 1.5s ease 0.3s infinite;">&#10095;</div>

      <!-- STAGE: LAYER STUDIO -->
      <div style="flex:0 0 100px;text-align:center;">
        <div style="width:50px;height:50px;margin:0 auto 4px;border-radius:10px;border:2px solid #ff4444;background:rgba(255,68,68,0.06);display:flex;align-items:center;justify-content:center;font-size:18px;">&#127910;</div>
        <div style="font-family:'Orbitron',sans-serif;font-size:6px;color:#ff4444;letter-spacing:1px;">LAYER IT</div>
      </div>

      <div style="flex:0 0 24px;color:#76b900;font-size:16px;animation:memeArrowPulse 1.5s ease 0.6s infinite;">&#10095;</div>

      <!-- STAGE: SOUND (IPFS) -->
      <div style="flex:0 0 100px;text-align:center;">
        <div style="width:50px;height:50px;margin:0 auto 4px;border-radius:10px;border:2px solid #8844ff;background:rgba(136,68,255,0.06);display:flex;align-items:center;justify-content:center;font-size:18px;">&#127925;</div>
        <div style="font-family:'Orbitron',sans-serif;font-size:6px;color:#8844ff;letter-spacing:1px;">SOUND &#8594; IPFS</div>
      </div>

      <div style="flex:0 0 24px;color:#76b900;font-size:16px;animation:memeArrowPulse 1.5s ease 0.9s infinite;">&#10095;</div>

      <!-- STAGE: YOUTUBE -->
      <div style="flex:0 0 100px;text-align:center;">
        <div style="width:50px;height:50px;margin:0 auto 4px;border-radius:10px;border:2px solid #ff0000;background:rgba(255,0,0,0.06);display:flex;align-items:center;justify-content:center;font-size:18px;">&#9654;</div>
        <div style="font-family:'Orbitron',sans-serif;font-size:6px;color:#ff0000;letter-spacing:1px;">YOUTUBE</div>
      </div>

      <div style="flex:0 0 24px;color:#76b900;font-size:16px;animation:memeArrowPulse 1.5s ease 1.2s infinite;">&#8634;</div>

    </div><!-- /row 2 -->

    <!-- LOOP LABEL -->
    <div style="font-family:'Press Start 2P',monospace;font-size:6px;color:rgba(118,185,0,0.4);letter-spacing:2px;margin-bottom:12px;">REPEAT &bull; GPU POWER &#8594; ART &#8594; CASH &bull; REPEAT</div>

  </div><!-- /factory pipeline -->

  <div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-bottom:14px;">
    <a href="/screensaver/" style="display:inline-block;padding:12px 24px;background:linear-gradient(135deg,#76b900,#8ec919);color:#fff;font-family:'Orbitron',sans-serif;font-size:11px;font-weight:900;letter-spacing:2px;border-radius:10px;text-decoration:none;box-shadow:0 4px 20px rgba(118,185,0,0.3);">SUPERCHARGE YOUR GPU</a>
    <a href="/imaginator/yt_upload.html" style="display:inline-block;padding:12px 24px;background:none;border:2px solid #ff4444;color:#ff4444;font-family:'Orbitron',sans-serif;font-size:11px;font-weight:900;letter-spacing:2px;border-radius:10px;text-decoration:none;">OPEN LAYER STUDIO</a>
  </div>

  <a class="kinetic-link" onclick="toggleSlideLibrary(this);return false;">HOW THE FACTORY WORKS &#9654;</a>

  <div class="slide-library" style="max-width:800px;margin:0 auto;">
    <div style="margin-top:20px;background:rgba(118,185,0,0.03);border:2px solid rgba(118,185,0,0.15);border-radius:16px;padding:24px 28px;text-align:left;">
      <div style="font-size:14px;color:#999;line-height:1.7;">
        <div><strong style="color:#fff;">1.</strong> Your GPU sits <strong style="color:#ff4444;">idle 90%</strong> of the time &mdash; the swarm puts it to work</div>
        <div><strong style="color:#fff;">2.</strong> Swarm <strong style="color:#76b900;">renders &amp; animates</strong> source images into art</div>
        <div><strong style="color:#fff;">3.</strong> Community votes &mdash; best art gets <strong style="color:#daa520;">batch sold</strong> on DeviantArt + ShortFactory</div>
        <div><strong style="color:#fff;">4.</strong> Art goes into <strong style="color:#ff4444;">Layer Studio</strong> &mdash; add sound via IPFS &mdash; publish to <strong style="color:#ff0000;">YouTube</strong></div>
        <div><strong style="color:#fff;">5.</strong> Direct <strong style="color:#daa520;">Monero payouts</strong> &mdash; no middleman, GPU power = cash</div>
      </div>
    </div>
  </div>
</div>
</div><!-- /hslide swarm -->

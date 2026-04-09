<div class="hslide" data-slide="comparison">
<!-- ═══ THE SHORT SUITE ZONE ═══ -->
<div class="suite-zone">
<div class="suite-zone-header" style="padding:8px 32px 0;">
  <div class="suite-badge" style="margin-bottom:4px;">THE SHORT SUITE</div>
</div>

<!-- COMPARISON: PHONES -->
<div class="compare-section" data-voice="See the difference. Their output versus ours.">
  <div class="compare-heading" style="margin-bottom:8px;font-size:clamp(20px,3vw,30px);">Their output vs <span style="color:#76b900;">ours</span>.</div>

  <div class="compare-stage">
    <!-- LEFT: REEEEEVID panel -->
    <div class="compare-brand-panel revid-panel">
      <div class="bp-name">REEEEEVID</div>
      <div class="bp-tag">BASIC TOOLS</div>
    </div>

    <!-- CAROUSEL -->
    <div style="flex:1;overflow:hidden;">
      <div class="compare-track" id="compareTrack">
        <!-- SLIDE 1: midgetHATE -->
        <div class="compare-slide">
          <div class="compare-pair">
            <div class="compare-side">
              <div class="compare-tag them">2D STILLS</div>
              <div class="compare-phone">
                <div class="compare-notch"></div>
                <div class="compare-screen">
                  <video id="mhStills" muted playsinline preload="metadata" loop>
                    <source src="/imaginator/marketplace/midgethate_stills.mp4?v=6" type="video/mp4">
                  </video>
                  <div class="brand-strip revid">REEEEEVID</div>
                  <div class="vm-ad" id="ad-mhStills"></div>
                </div>
              </div>
              <div class="compare-song">midgetHATE</div>
            </div>
            <div class="compare-vs">VS</div>
            <div class="compare-side">
              <div class="compare-tag us">ANIMATED</div>
              <div class="compare-phone winner">
                <div class="compare-notch"></div>
                <div class="compare-screen">
                  <video id="mhAnim" muted playsinline preload="metadata" loop>
                    <source src="/imaginator/marketplace/midgethate_animated.mp4?v=6" type="video/mp4">
                  </video>
                  <div class="brand-strip sf">SHORTFACTORY</div>
                  <div class="kinetic-overlay" id="kineticMH"><div class="graf-comp" id="grafMH"></div></div>
                  <img src="/imaginator/Sf.gif" class="sf-logo-mark" alt="SF">
                  <div class="vm-ad" id="ad-mhAnim"></div>
                </div>
              </div>
              <div class="compare-song">midgetHATE 3D</div>
            </div>
          </div>
        </div>

        <!-- SLIDE 2: GIANTlove -->
        <div class="compare-slide">
          <div class="compare-pair">
            <div class="compare-side">
              <div class="compare-tag them">2D STILLS</div>
              <div class="compare-phone">
                <div class="compare-notch"></div>
                <div class="compare-screen">
                  <video id="glStills" muted playsinline preload="metadata" loop>
                    <source src="/imaginator/marketplace/giantlove_stills.mp4?v=6" type="video/mp4">
                  </video>
                  <div class="brand-strip revid">REEEEEVID</div>
                  <div class="vm-ad" id="ad-glStills"></div>
                </div>
              </div>
              <div class="compare-song">GIANTlove</div>
            </div>
            <div class="compare-vs">VS</div>
            <div class="compare-side">
              <div class="compare-tag us">ANIMATED</div>
              <div class="compare-phone winner">
                <div class="compare-notch"></div>
                <div class="compare-screen">
                  <video id="glAnim" muted playsinline preload="metadata" loop>
                    <source src="/imaginator/marketplace/giantlove_animated.mp4?v=6" type="video/mp4">
                  </video>
                  <div class="brand-strip sf">SHORTFACTORY</div>
                  <div class="kinetic-overlay" id="kineticGL"><div class="graf-comp" id="grafGL"></div></div>
                  <img src="/imaginator/Sf.gif" class="sf-logo-mark" id="glAnimLogo" style="display:none;" alt="SF">
                  <div class="vm-ad" id="ad-glAnim"></div>
                </div>
              </div>
              <div class="compare-song">GIANTlove 3D</div>
            </div>
          </div>
        </div>

        <!-- SLIDE 3: Imaginator CTA -->
        <div class="compare-slide">
          <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:480px;gap:20px;padding:40px;">
            <div style="font-family:'Orbitron',sans-serif;font-size:clamp(28px,4vw,42px);font-weight:900;background:linear-gradient(135deg,#FFD700,#FF6B35);-webkit-background-clip:text;background-clip:text;color:transparent;letter-spacing:3px;">THE IMAGINATOR</div>
            <div style="font-size:18px;color:#666;max-width:500px;line-height:1.6;">Turn your stills into cinematic animated shorts. Crowdsourced animation. VidMan polish. One click to YouTube.</div>
            <a href="/imaginator/index2.php" style="display:inline-block;padding:18px 48px;background:linear-gradient(135deg,#FFD700,#FF6B35);border-radius:14px;font-family:'Orbitron',sans-serif;font-weight:900;font-size:16px;color:#000;letter-spacing:3px;text-decoration:none;box-shadow:0 8px 32px rgba(255,215,0,0.3);transition:all 0.3s;">TRY IT FREE</a>
            <div style="font-size:12px;color:#aaa;">5 free tokens on signup. No credit card.</div>
          </div>
        </div>
      </div>
    </div>

    <!-- RIGHT: SHORTFACTORY panel -->
    <div class="compare-brand-panel sf-panel">
      <div class="bp-name">SHORTFACTORY</div>
      <div class="bp-tag">CINEMA ENGINE</div>
    </div>
  </div>

  <div class="compare-dots" id="compareDots">
    <button class="compare-dot active" onclick="goSlide(0)" title="midgetHATE"></button>
    <button class="compare-dot" onclick="goSlide(1)" title="GIANTlove"></button>
    <button class="compare-dot dot-cta" onclick="goSlide(2)"></button>
  </div>

  <audio id="audioMH" preload="metadata" loop>
    <source src="/imaginator/marketplace/midgethate.mp3" type="audio/mpeg">
  </audio>
  <audio id="audioGL" preload="metadata" loop>
    <source src="/imaginator/marketplace/giantlove.mp3" type="audio/mpeg">
  </audio>

  <div class="compare-controls">
    <button class="compare-playbtn" id="comparePlayBtn" onclick="toggleCompare()">&#9654; Play Comparison</button>
    <button class="vidman-toggle" id="vidmanBtn" onclick="toggleVidMan()">VIDMAN: OFF</button>
    <button class="kinetic-toggle" id="kineticBtn" onclick="toggleKinetic()">KINETIC: OFF</button>
    <button class="mute-toggle" id="muteBtn" onclick="toggleMute()" title="Toggle audio">&#128263;</button>
    <button class="forms-btn" disabled>mcFORMS<span class="coming">COMING SOON</span></button>
    <div class="compare-time" id="compareTime"></div>
  </div>
  <div class="compare-verdict">Same stills. Same songs. <strong>Cinema.</strong></div>
</div>
</div><!-- /suite-zone (comparison only) -->
</div><!-- /hslide comparison -->

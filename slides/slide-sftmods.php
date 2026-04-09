<div class="hslide" data-slide="sftmods">
<div class="section" style="text-align:center;background:linear-gradient(165deg,#0a0800 0%,#0d0a05 40%,#0a0a0a 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;box-sizing:border-box;" data-voice="SFT Mods. Upload your game mods. Earn contribution credits. Your work, your receipt.">

  <div style="font-family:'Press Start 2P',monospace;font-size:9px;color:#ff8800;letter-spacing:3px;margin-bottom:6px;">MODDER ZONE</div>
  <div style="font-size:clamp(24px,4vw,38px);font-weight:900;color:#fff;line-height:1.2;margin-bottom:8px;">SFT <span style="color:#0f8;">MODS</span></div>
  <div style="font-family:'Courier New',monospace;font-size:12px;color:#666;margin-bottom:28px;">Upload room layouts. Get your receipt. Earn credits.</div>

  <!-- UPLOAD BOX -->
  <div style="max-width:400px;width:90%;margin:0 auto;">
    <div style="border:2px dashed #0f8;border-radius:12px;padding:32px 20px;background:rgba(0,255,136,.02);cursor:pointer;transition:all .3s;" id="sftDropZone" onclick="document.getElementById('sftFileInput').click()" onmouseover="this.style.borderColor='#fc0';this.style.background='rgba(255,204,0,.04)'" onmouseout="this.style.borderColor='#0f8';this.style.background='rgba(0,255,136,.02)'">
      <input type="file" id="sftFileInput" accept=".sft" style="display:none" onchange="handleSftUpload(event)">
      <div style="font-size:42px;margin-bottom:12px;">&#128230;</div>
      <div style="font-family:'Press Start 2P',monospace;font-size:9px;color:#0f8;margin-bottom:8px;">DROP .SFT FILE HERE</div>
      <div style="font-family:'Courier New',monospace;font-size:11px;color:#555;">or click to browse</div>
    </div>

    <!-- RECEIPT PREVIEW (hidden until upload) -->
    <div id="sftPreview" style="display:none;margin-top:20px;background:rgba(0,0,0,.6);border:1px solid #1a3a1a;border-radius:8px;padding:16px;text-align:left;font-family:'Press Start 2P',monospace;font-size:7px;">
      <div style="color:#0f8;font-size:9px;text-align:center;margin-bottom:10px;">RECEIPT VERIFIED</div>
      <div style="color:#fc0;font-size:12px;text-align:center;margin-bottom:10px;letter-spacing:2px;" id="sftUpCode"></div>
      <div style="color:#888;">ROOM: <span id="sftUpRoom" style="color:#ccc;"></span></div>
      <div style="color:#888;">HOUSE: <span id="sftUpHouse" style="color:#ccc;"></span></div>
      <div style="color:#888;">MODDER: <span id="sftUpModder" style="color:#fc0;"></span></div>
      <div style="color:#888;margin-top:6px;">ITEMS: <span id="sftUpItems" style="color:#0f8;"></span> &bull; TYPES: <span id="sftUpTypes" style="color:#0f8;"></span> &bull; SCORE: <span id="sftUpScore" style="color:#0f8;"></span>/100</div>
      <div style="margin-top:10px;text-align:center;">
        <div style="color:#4af;font-size:6px;">CONTRIBUTION CREDITS APPLIED</div>
        <div id="sftUpTags" style="color:#0f8;margin-top:4px;"></div>
      </div>
    </div>
  </div>

  <!-- ROYALTY CALCULATOR -->
  <a class="kinetic-link" onclick="toggleSlideLibrary(this);return false;" style="margin-top:20px;">CALCULATE ROYALTIES &#9654;</a>
  <div class="slide-library" style="max-width:500px;margin:0 auto;">
    <div id="royCalcHome" style="margin-top:20px;padding:20px;background:rgba(0,255,136,.02);border:1px solid rgba(0,255,136,.08);border-radius:12px;text-align:left;">
      <div style="font-family:'Press Start 2P',monospace;font-size:7px;color:#fc0;letter-spacing:2px;text-align:center;margin-bottom:14px;">ROYALTY CALCULATOR</div>

      <div style="margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;font-size:11px;"><span style="color:#888;">Monthly Players</span><span id="rcPlayers" style="color:#fc0;font-weight:700;">10,000</span></div>
        <input type="range" min="1000" max="500000" step="1000" value="10000" oninput="updateRoyCalcHome()" id="rcSlide1" style="width:100%;accent-color:#ff8800;margin-top:4px;">
      </div>

      <div style="margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;font-size:11px;"><span style="color:#888;">Paying %</span><span id="rcPaying" style="color:#fc0;font-weight:700;">5%</span></div>
        <input type="range" min="1" max="30" step="1" value="5" oninput="updateRoyCalcHome()" id="rcSlide2" style="width:100%;accent-color:#ff8800;margin-top:4px;">
      </div>

      <div style="margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;font-size:11px;"><span style="color:#888;">Avg Spend</span><span id="rcSpend" style="color:#fc0;font-weight:700;">&pound;2.99</span></div>
        <input type="range" min="99" max="999" step="50" value="299" oninput="updateRoyCalcHome()" id="rcSlide3" style="width:100%;accent-color:#ff8800;margin-top:4px;">
      </div>

      <div style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;font-size:11px;"><span style="color:#888;">Active Modders</span><span id="rcModders" style="color:#fc0;font-weight:700;">50</span></div>
        <input type="range" min="5" max="1000" step="5" value="50" oninput="updateRoyCalcHome()" id="rcSlide4" style="width:100%;accent-color:#ff8800;margin-top:4px;">
      </div>

      <div style="border-top:1px solid rgba(255,136,0,.15);padding-top:12px;">
        <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:6px;"><span style="color:#888;">Gross Revenue</span><span id="rcGross" style="color:#0f8;font-weight:700;">&pound;1,495</span></div>
        <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:6px;"><span style="color:#888;">Modder Pool (15%)</span><span id="rcPool" style="color:#fc0;font-weight:700;">&pound;224</span></div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;"><span style="color:#fff;font-weight:700;">YOUR MONTHLY CUT</span><span id="rcYours" style="color:#0f8;font-weight:700;font-size:15px;">&pound;4.48</span></div>
        <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px;"><span style="color:#555;">Platform keeps (85%)</span><span id="rcPlatform" style="color:#666;">&pound;1,271</span></div>
        <div style="display:flex;justify-content:space-between;font-size:11px;"><span style="color:#555;">Yearly (you)</span><span id="rcYearly" style="color:#666;">&pound;54</span></div>
      </div>

      <div style="margin-top:14px;padding:10px;background:rgba(255,136,0,.04);border:1px solid rgba(255,136,0,.08);border-radius:8px;font-size:10px;color:#666;line-height:1.6;text-align:center;">
        Build rooms &bull; Upload SFT receipts &bull; Earn royalties<br>
        Sound effects &bull; Sprites &bull; Rooms &mdash; everything earns<br>
        <a href="/trump/game/cat/" style="color:#ff8800;text-decoration:none;font-weight:700;">PLAY CAT MAYHEM &rarr;</a>
      </div>
    </div>
  </div>

</div>
</div><!-- /hslide sftmods -->

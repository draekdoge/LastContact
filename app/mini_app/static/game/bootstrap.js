/**
 * Загрузка manifest.json, тема, Lottie/image слоты, спонсорские вставки.
 * Ассеты клади в /game/assets/... и пропиши путь в manifest (относительно /game/).
 */
(function () {
  var BASE = "/game/";

  function el(q) {
    return document.querySelector(q);
  }

  function all(q) {
    return Array.prototype.slice.call(document.querySelectorAll(q));
  }

  function joinUrl(rel) {
    if (!rel || !String(rel).trim()) return "";
    var s = String(rel).trim();
    if (/^https?:\/\//i.test(s)) return s;
    var r = s.replace(/^\/+/, "");
    return BASE + r;
  }

  function applyTheme(theme) {
    if (!theme) return;
    var root = document.documentElement;
    if (theme.accent) root.style.setProperty("--game-accent", theme.accent);
    if (theme.accentDim) root.style.setProperty("--game-accent-dim", theme.accentDim);
    if (theme.bg) root.style.setProperty("--game-bg", theme.bg);
    if (theme.text) root.style.setProperty("--game-text", theme.text);
  }

  function mountLottie(slot, relPath, opts) {
    var host =
      el('[data-game-lottie-slot="' + slot + '"]') ||
      el("#gameHost" + slot.charAt(0).toUpperCase() + slot.slice(1));
    if (!host) return;
    var url = joinUrl(relPath);
    if (!url) {
      host.setAttribute("hidden", "");
      host.innerHTML = "";
      return;
    }
    host.removeAttribute("hidden");
    host.innerHTML = "";
    var LP = window.customElements && customElements.get("lottie-player");
    if (!LP) {
      var imgFallback = joinUrl(opts && opts.fallbackImage);
      if (imgFallback) {
        var im = document.createElement("img");
        im.src = imgFallback;
        im.alt = "";
        im.className = "game-fallback-img";
        host.appendChild(im);
      }
      return;
    }
    var player = document.createElement("lottie-player");
    player.setAttribute("src", url);
    player.setAttribute("background", "transparent");
    player.setAttribute("speed", String((opts && opts.speed) || 1));
    if (opts && opts.loop === false) player.setAttribute("count", "1");
    else player.setAttribute("loop", "");
    player.setAttribute("autoplay", "");
    host.appendChild(player);
  }

  function mountImage(slot, relPath) {
    var host = el('[data-game-image-slot="' + slot + '"]');
    if (!host) return;
    var url = joinUrl(relPath);
    if (!url) {
      host.setAttribute("hidden", "");
      host.innerHTML = "";
      return;
    }
    host.removeAttribute("hidden");
    host.innerHTML = "";
    var im = document.createElement("img");
    im.src = url;
    im.alt = "";
    im.className = "game-image-slot-img";
    host.appendChild(im);
  }

  function renderSponsorSlots(manifest) {
    var prog = manifest.progression || {};
    var slots = prog.sponsorSlots || [];
    slots.forEach(function (slot) {
      if (!slot || !slot.enabled) return;
      var mount =
        el('[data-sponsor-slot="' + slot.id + '"]') ||
        el("#gameSponsor" + slot.id.replace(/[^a-zA-Z0-9]/g, "_"));
      if (!mount) return;
      mount.removeAttribute("hidden");
      if (slot.kind === "html" && slot.html) {
        mount.innerHTML = String(slot.html);
        return;
      }
      if (slot.kind === "banner" && slot.assetUrl) {
        var wrap = document.createElement("div");
        wrap.className = "game-sponsored-inner";
        var a = document.createElement("a");
        a.href = slot.href || "#";
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        var im = document.createElement("img");
        im.src = joinUrl(slot.assetUrl);
        im.alt = slot.label || "sponsor";
        a.appendChild(im);
        wrap.appendChild(a);
        if (slot.label) {
          var cap = document.createElement("div");
          cap.className = "game-sponsored-label";
          cap.textContent = slot.label;
          wrap.appendChild(cap);
        }
        mount.appendChild(wrap);
      }
    });
  }

  function maybeRemoteConfig(manifest) {
    var prog = manifest.progression || {};
    var u = prog.remoteConfigUrl;
    if (!u || !String(u).trim()) return;
    var sec = Number(prog.remoteConfigPollSeconds) || 0;
    function pull() {
      fetch(u, { cache: "no-store" })
        .then(function (r) {
          return r.ok ? r.json() : null;
        })
        .then(function (patch) {
          if (!patch || typeof patch !== "object") return;
          if (patch.theme) applyTheme(patch.theme);
          if (patch.lottie) {
            Object.keys(patch.lottie).forEach(function (k) {
              mountLottie(k, patch.lottie[k], {});
            });
          }
          if (patch.progression && Array.isArray(patch.progression.sponsorSlots)) {
            renderSponsorSlots({ progression: patch.progression });
          }
        })
        .catch(function () {});
    }
    pull();
    if (sec > 10) setInterval(pull, sec * 1000);
  }

  window.GameShell = window.GameShell || {};
  window.GameShell.basePath = BASE;
  window.GameShell.reload = function () {
    init();
  };

  function init() {
    fetch(joinUrl("manifest.json"), { cache: "no-store" })
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (manifest) {
        if (!manifest) return;
        window.GameShell.manifest = manifest;
        applyTheme(manifest.theme);
        var lot = manifest.lottie || {};
        var imgs = manifest.images || {};
        Object.keys(lot).forEach(function (key) {
          var fb = key === "statusHero" ? imgs.statusHeroFallback : "";
          mountLottie(key, lot[key], { fallbackImage: fb });
        });
        mountImage("worldMapOverlay", imgs.worldMapOverlay);
        renderSponsorSlots(manifest);
        maybeRemoteConfig(manifest);
      })
      .catch(function () {});
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

import { useCallback, useEffect, useRef, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, AreaChart, Area,
} from "recharts";
import {
  aiAssistant,
  createComment,
  createPost,
  fetchComments,
  fetchCreators,
  fetchFeed,
  fetchGamification,
  fetchWellbeing,
  fetchTrending,
  previewAnalysis,
  toggleLike,
  toggleBookmark,
  reportPost,
  summarizeContent,
  registerUser,
  loginUser,
  fetchMe,
  editPost,
  deletePost,
  searchContent,
  updateProfile,
} from "./api";
import "./App.css";

const MODES = [
  { id: "odak", label: "Odak", hint: "Sakin, yapılandırılmış, düşük gürültü" },
  { id: "ogrenme", label: "Öğrenme", hint: "Açıklayıcı ve kavram yoğun içerik" },
  { id: "eglence", label: "Eğlence", hint: "Hafif, sosyal, toksik olmayan keyif" },
];

const SOCIAL_LINKS = [
  { label: "Instagram", icon: "📷", url: "https://instagram.com/meridyen" },
  { label: "X (Twitter)", icon: "𝕏", url: "https://x.com/meridyen" },
  { label: "YouTube", icon: "▶", url: "https://youtube.com/@meridyen" },
  { label: "LinkedIn", icon: "in", url: "https://linkedin.com/company/meridyen" },
  { label: "TikTok", icon: "♪", url: "https://tiktok.com/@meridyen" },
];

const AI_SUGGESTIONS = [
  { icon: "✦", text: "Gönderimi özetle — ana fikri kısa tut" },
  { icon: "◈", text: "İçeriğimi daha erişilebilir yap" },
  { icon: "△", text: "Bu konuda trend olan yaklaşımı bul" },
  { icon: "◐", text: "Hedef kitleme uygun başlık öner" },
];

const TIP_OPTIONS = [
  { amount: 10, label: "Minik destek" },
  { amount: 25, label: "Güzel bir jest" },
  { amount: 50, label: "Cömert destek" },
];

const SUB_TIERS = [
  { name: "Bronz", desc: "Aylık destekçi", price: "29₺/ay" },
  { name: "Gümüş", desc: "Özel içerik + öncelik", price: "59₺/ay" },
  { name: "Altın", desc: "Tam erişim + mentorluk", price: "99₺/ay" },
];

const ONBOARDING_STEPS = [
  { icon: "◈", title: "Hoş Geldin!", text: "Meridyen, dijital denge odaklı yeni nesil sosyal medya platformu. İçeriklerini güvenle paylaş, toplulukla bağlantı kur." },
  { icon: "◐", title: "Modunu Seç", text: "Odak, Öğrenme veya Eğlence modunu seçerek akışını kişiselleştir. Yapay zekâ içeriklerini sana göre sıralasın." },
  { icon: "✦", title: "Yapay Zekâ Desteği", text: "AI asistanın içeriklerini analiz eder, öneriler sunar ve dijital dengeni korumana yardımcı olur." },
];

const REPORT_REASONS = [
  "Yanlış bilgi / dezenformasyon",
  "Zararlı veya tehlikeli içerik",
  "Taciz veya şiddet içeren dil",
  "Spam veya yanıltıcı reklam",
  "Telif hakkı ihlali",
  "Diğer",
];

const SCENARIOS = [
  { step: 1, title: "Yeni Kullanıcı Kaydı", text: "Kullanıcı platforma gelir, 3 adımlık onboarding akışını tamamlar ve tercih ettiği modu seçer. Profili otomatik oluşturulur." },
  { step: 2, title: "Akış Keşfi", text: "Seçilen moda göre kişiselleştirilmiş akış sunulur. Her içerik的安全lık, fayda ve ton açısından AI tarafından sıralanmıştır." },
  { step: 3, title: "İçerik Üretimi", text: "Kullanıcı compose alanından metin veya fotoğraf paylaşır. İçerik gerçek zamanlı analiz edilir ve anında akışa eklenir." },
  { step: 4, title: "Etkileşim", text: "Beğeni, yorum, bahşiş ve abonelik ile içerik üreticilerini destekler. Her etkileşim oyunlaştırma puanı kazandırır." },
  { step: 5, title: "Denge Raporu", text: "Kullanıcı dijital denge durumunu, oturum istatistiklerini ve güvenli içerik oranını gerçek zamanlı takip eder." },
  { step: 6, title: "Gelir Paylaşımı", text: "İçerik üreticileri,/refah skorları ve görünürlük çarpanlarına göre adil bir gelir paylaşımından faydalanır." },
  { step: 7, title: "Topluluk Güvenliği", text: "AI destekli moderasyon, toksik ve spam içerikleri otomatik filtreler. Kullanıcılar endişeli içerikleri raporlayabilir." },
];

const PAGES = [
  { id: "akis", label: "Akış", icon: "◈" },
  { id: "denge", label: "Denge", icon: "◐" },
  { id: "uretici", label: "Üretici", icon: "△" },
  { id: "profil", label: "Profil", icon: "◉" },
  { id: "senaryolar", label: "Senaryolar", icon: "◆" },
];

function formatTime(value) {
  if (!value) return "Az önce";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "Az önce";
  return d.toLocaleString("tr-TR", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

function relativeTime(value) {
  if (!value) return "Az önce";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  const diff = Date.now() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Az önce";
  if (mins < 60) return `${mins} dk önce`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} saat önce`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days} gün önce`;
  return d.toLocaleString("tr-TR", { day: "numeric", month: "short" });
}

const CHART_COLORS = {
  primary: "#6366f1",
  accent: "#f59e0b",
  success: "#10b981",
  danger: "#ef4444",
  purple: "#8b5cf6",
  pink: "#ec4899",
  cyan: "#06b6d4",
  teal: "#14b8a6",
};

const CATEGORIES = ["Tümü", "Eğitim", "Teknoloji", "Bilim", "Sanat", "Spor", "Genel"];

const AVATAR_COLORS = [
  ["#4f6ef7", "#818cf8"],
  ["#ec4899", "#f472b6"],
  ["#10b981", "#34d399"],
  ["#f59e0b", "#fbbf24"],
  ["#8b5cf6", "#a78bfa"],
  ["#ef4444", "#f87171"],
  ["#06b6d4", "#22d3ee"],
  ["#14b8a6", "#2dd4bf"],
];

function getAvatarColor(name) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

function Avatar({ name, size = 36, className = "" }) {
  const [bg, fg] = getAvatarColor(name);
  const initial = (name || "?")[0].toUpperCase();
  return (
    <div
      className={`avatar ${className}`}
      style={{
        width: size,
        height: size,
        minWidth: size,
        borderRadius: size * 0.28,
        background: `linear-gradient(135deg, ${bg}, ${fg})`,
        border: "none",
        color: "#fff",
        fontSize: size * 0.4,
        lineHeight: 1,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        overflow: "hidden",
        flexShrink: 0,
      }}
    >
      {initial}
    </div>
  );
}

async function compressImage(file, maxWidth = 1200, quality = 0.8) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        let w = img.width;
        let h = img.height;
        if (w > maxWidth) {
          h = Math.round((h / w) * maxWidth);
          w = maxWidth;
        }
        canvas.width = w;
        canvas.height = h;
        canvas.getContext("2d").drawImage(img, 0, 0, w, h);
        resolve(canvas.toDataURL("image/jpeg", quality));
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

/* ═══════════════════════════════════════════════════════════════════════════
   AUTH PAGE
   ═══════════════════════════════════════════════════════════════════════════ */

function AuthPage({ onAuth }) {
  const [tab, setTab] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [category, setCategory] = useState("Genel");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function reset() {
    setUsername("");
    setPassword("");
    setDisplayName("");
    setBio("");
    setCategory("Genel");
    setError("");
  }

  function switchTab(t) {
    reset();
    setTab(t);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!username.trim() || !password.trim()) {
      setError("Kullanıcı adı ve şifre zorunludur.");
      return;
    }

    if (username.trim().length < 3) {
      setError("Kullanıcı adı en az 3 karakter olmalıdır.");
      return;
    }

    if (password.trim().length < 6) {
      setError("Şifre en az 6 karakter olmalıdır.");
      return;
    }

    if (tab === "register") {
      if (!displayName.trim()) {
        setError("Görünen ad zorunludur.");
        return;
      }
      if (displayName.trim().length < 2) {
        setError("Görünen ad en az 2 karakter olmalıdır.");
        return;
      }
    }

    setBusy(true);
    try {
      let result;
      if (tab === "login") {
        result = await loginUser({ username: username.trim(), password: password.trim() });
      } else {
        result = await registerUser({
          username: username.trim(),
          password: password.trim(),
          display_name: displayName.trim(),
          bio: bio.trim(),
          category,
        });
      }
      const user = result.user || { username: result.username, display_name: result.display_name || result.username };
      const token = result.access_token || result.token;
      if (token) {
        localStorage.setItem("meridyen-token", token);
      }
      localStorage.setItem("meridyen-user", JSON.stringify(user));
      onAuth(user, token);
    } catch (err) {
      setError(err.message || "Bir hata oluştu. Lütfen tekrar deneyin.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-bg-orb auth-bg-orb-1" />
      <div className="auth-bg-orb auth-bg-orb-2" />
      <div className="auth-bg-orb auth-bg-orb-3" />

      <div className="auth-card">
        <div className="auth-brand">
          <img className="auth-logo" src="/meridyen-logo.png" alt="Meridyen" />
          <h1 className="auth-title">Meridyen</h1>
          <p className="auth-subtitle">Dijital denge platformu</p>
        </div>

        <div className="auth-tabs">
          <button
            className={`auth-tab${tab === "login" ? " active" : ""}`}
            onClick={() => switchTab("login")}
            type="button"
          >
            Giriş Yap
          </button>
          <button
            className={`auth-tab${tab === "register" ? " active" : ""}`}
            onClick={() => switchTab("register")}
            type="button"
          >
            Kayıt Ol
          </button>
          <div className={`auth-tab-indicator${tab === "register" ? " right" : ""}`} />
        </div>

        {error && (
          <div className="auth-error" role="alert">
            <span className="auth-error-icon">✕</span>
            {error}
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-field">
            <label className="auth-label" htmlFor="auth-username">Kullanıcı Adı</label>
            <input
              id="auth-username"
              className="auth-input"
              type="text"
              placeholder="kullanici_adi"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              autoFocus
            />
          </div>

          {tab === "register" && (
            <>
              <div className="auth-field">
                <label className="auth-label" htmlFor="auth-display-name">Görünen Ad</label>
                <input
                  id="auth-display-name"
                  className="auth-input"
                  type="text"
                  placeholder="Ad Soyad"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  autoComplete="name"
                />
              </div>
            </>
          )}

          <div className="auth-field">
            <label className="auth-label" htmlFor="auth-password">Şifre</label>
            <input
              id="auth-password"
              className="auth-input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={tab === "login" ? "current-password" : "new-password"}
            />
          </div>

          {tab === "register" && (
            <>
              <div className="auth-field">
                <label className="auth-label" htmlFor="auth-bio">Biyografi (isteğe bağlı)</label>
                <input
                  id="auth-bio"
                  className="auth-input"
                  type="text"
                  placeholder="Kendinden kısaca bahset..."
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  maxLength={200}
                />
              </div>

              <div className="auth-field">
                <label className="auth-label" htmlFor="auth-category">İlgi Alanı</label>
                <select
                  id="auth-category"
                  className="auth-select"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  {CATEGORIES.filter((c) => c !== "Tümü").map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </>
          )}

          <button type="submit" className="auth-submit" disabled={busy}>
            {busy ? (
              <span className="auth-spinner" />
            ) : tab === "login" ? (
              "Giriş Yap"
            ) : (
              "Kayıt Ol"
            )}
          </button>
        </form>

        <div className="auth-footer-text">
          {tab === "login" ? (
            <span>
              Hesabın yok mu?{" "}
              <button type="button" className="auth-link" onClick={() => switchTab("register")}>
                Kayıt ol
              </button>
            </span>
          ) : (
            <span>
              Zaten hesabın var mı?{" "}
              <button type="button" className="auth-link" onClick={() => switchTab("login")}>
                Giriş yap
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   APP
   ═══════════════════════════════════════════════════════════════════════════ */

function App() {
  const [theme, setTheme] = useState(() => {
    try { return localStorage.getItem("meridyen-theme") || "light"; } catch { return "light"; }
  });
  const [mode, setMode] = useState("odak");
  const [page, setPage] = useState("akis");
  const [posts, setPosts] = useState([]);
  const [creators, setCreators] = useState([]);
  const [wellbeing, setWellbeing] = useState(null);
  const [gamification, setGamification] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [startedAt] = useState(() => Date.now());
  const [modeSwitches, setModeSwitches] = useState(0);
  const [sessionMinutes, setSessionMinutes] = useState(0);
  const [showAI, setShowAI] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [tipPost, setTipPost] = useState(null);
  const [subPost, setSubPost] = useState(null);
  const [showNotif, setShowNotif] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, type: "system", text: "Meridyen'e hoş geldin! Akışını keşfetmeye başla.", time: new Date().toISOString(), read: false },
    { id: 2, type: "follow", text: "<strong>Ayşe Kaya</strong> seni takip etmeye başladı.", time: new Date(Date.now() - 120000).toISOString(), read: false },
    { id: 3, type: "like", text: "<strong>Mehmet Ö.</strong> gönderini beğendi.", time: new Date(Date.now() - 900000).toISOString(), read: false },
  ]);
  const [notifSound, setNotifSound] = useState(() => {
    try { return localStorage.getItem("meridyen-notif-sound") !== "off"; } catch { return true; }
  });
  const [toasts, setToasts] = useState([]);
  const [showOnboarding, setShowOnboarding] = useState(() => {
    try { return !localStorage.getItem("meridyen-onboarded"); } catch { return true; }
  });
  const [reportPost_, setReportPost] = useState(null);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = localStorage.getItem("meridyen-user");
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });
  const [authToken, setAuthToken] = useState(() => {
    try { return localStorage.getItem("meridyen-token"); } catch { return null; }
  });
  const [authChecking, setAuthChecking] = useState(true);

  const USERNAME = currentUser?.username || "meridyen_user";

  useEffect(() => {
    let cancelled = false;
    async function check() {
      const token = localStorage.getItem("meridyen-token");
      if (!token) {
        setAuthChecking(false);
        return;
      }
      try {
        const me = await fetchMe();
        if (!cancelled) {
          const user = me.user || me;
          setCurrentUser(user);
          setAuthToken(token);
          localStorage.setItem("meridyen-user", JSON.stringify(user));
        }
      } catch {
        if (!cancelled) {
          localStorage.removeItem("meridyen-token");
          localStorage.removeItem("meridyen-user");
          setCurrentUser(null);
          setAuthToken(null);
        }
      } finally {
        if (!cancelled) setAuthChecking(false);
      }
    }
    check();
    return () => { cancelled = true; };
  }, []);

  function handleAuth(user, token) {
    setCurrentUser(user);
    setAuthToken(token);
  }

  function handleLogout() {
    localStorage.removeItem("meridyen-token");
    localStorage.removeItem("meridyen-user");
    setCurrentUser(null);
    setAuthToken(null);
  }

  function addToast(text, type = "info") {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, text, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.map((t) => t.id === id ? { ...t, exit: true } : t));
      setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 400);
    }, 3500);
  }

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("meridyen-theme", theme); } catch {}
  }, [theme]);

  useEffect(() => {
    if (!showNotif) return;
    function close(e) {
      if (!e.target.closest(".notif-wrapper")) setShowNotif(false);
    }
    document.addEventListener("click", close, true);
    return () => document.removeEventListener("click", close, true);
  }, [showNotif]);

  useEffect(() => {
    function onKey(e) {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      if (showAI || showOnboarding || showShortcuts || reportPost_ || tipPost || subPost) return;
      const key = e.key.toLowerCase();
      if (key === "d" && e.shiftKey) { setTheme((t) => t === "dark" ? "light" : "dark"); }
      else if (key === "1") { setPage("akis"); }
      else if (key === "2") { setPage("denge"); }
      else if (key === "3") { setPage("uretici"); }
      else if (key === "4") { setPage("profil"); }
      else if (key === "a" && !e.ctrlKey && !e.metaKey) { setShowAI(true); }
      else if (key === "escape") { setShowAI(false); setShowShortcuts(false); setReportPost(null); setTipPost(null); setSubPost(null); }
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [showAI, showOnboarding, showShortcuts, reportPost_, tipPost, subPost]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [feed, economy, snapshot, gameData] = await Promise.all([
        fetchFeed(mode, USERNAME),
        fetchCreators(mode),
        fetchWellbeing(mode),
        fetchGamification(USERNAME),
      ]);
      setPosts(feed);
      setCreators(economy.creators || []);
      setWellbeing(snapshot);
      setGamification(gameData);
    } catch {
      setMessage("Sunucuya bağlanılamadı. Backend'in çalıştığından emin olun.");
    } finally {
      setLoading(false);
    }
  }, [mode, currentUser?.username]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const t = window.setInterval(() => {
      setSessionMinutes(Math.max(1, Math.round((Date.now() - startedAt) / 60000)));
    }, 15000);
    return () => window.clearInterval(t);
  }, [startedAt]);

  function changeMode(next) {
    if (next === mode) return;
    setMode(next);
    setModeSwitches((c) => c + 1);
    setMessage(`${MODES.find((m) => m.id === next)?.label} moduna geçildi.`);
  }

  const currentMode = MODES.find((m) => m.id === mode);

  if (authChecking) {
    return (
      <div className="auth-page">
        <div className="auth-bg-orb auth-bg-orb-1" />
        <div className="auth-bg-orb auth-bg-orb-2" />
        <div className="auth-bg-orb auth-bg-orb-3" />
        <div className="auth-loading-center">
          <span className="auth-spinner-lg" />
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return <AuthPage onAuth={handleAuth} />;
  }

  return (
    <div className="shell" data-mode={mode}>
      <a href="#main-content" className="skip-link">İçeriğe atla</a>
      {sidebarOpen && <div className="sidebar-backdrop" onClick={() => setSidebarOpen(false)} />}

      <aside className={`sidebar${sidebarOpen ? " open" : ""}`} aria-label="Ana menü">
        <div className="brand">
          <img className="brand-logo" src="/meridyen-logo.png" alt="Meridyen" />
          <div className="brand-text">
            <h1>Meridyen</h1>
            <span>Dijital denge platformu</span>
          </div>
        </div>

        <nav className="nav-section">
          <span className="nav-label">Gezinti</span>
          <ul className="nav-list">
            {PAGES.map((item) => (
              <li key={item.id}>
                <button
                  className={`nav-item${page === item.id ? " active" : ""}`}
                  onClick={() => { setPage(item.id); setSidebarOpen(false); }}
                  aria-current={page === item.id ? "page" : undefined}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span className="nav-text">{item.label}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {wellbeing && (
          <div className="sidebar-card" style={{ animationDelay: "0.15s" }}>
            <p className="sidebar-card-label">Akış dengesi</p>
            <div className="score-display">
              <span className="score-number">{wellbeing.score ?? "—"}</span>
              <span className="score-total">/ 100</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${wellbeing.score || 0}%` }} />
            </div>
            <small>{wellbeing.suppressed_count || 0} içerik filtrelendi</small>
          </div>
        )}

        {gamification && (
          <div className="sidebar-card game-card" style={{ animationDelay: "0.25s" }}>
            <div className="game-level-row">
              <span className="level-badge">Lv.{gamification.level}</span>
              <div className="xp-section">
                <div className="xp-bar">
                  <div className="xp-fill" style={{ width: `${(gamification.xp / gamification.xp_for_next) * 100}%` }} />
                </div>
                <span className="xp-text">{gamification.xp}/{gamification.xp_for_next} XP</span>
              </div>
            </div>
            <div className="game-stats">
              <div className="game-stat-item">
                <span className="game-stat-icon">△</span>
                <div>
                  <span className="game-stat-value">{gamification.streak}</span>
                  <span className="game-stat-label"> gün streak</span>
                </div>
              </div>
              <div className="game-stat-item">
                <span className="game-stat-icon">✦</span>
                <div>
                  <span className="game-stat-value">{gamification.badge_count}</span>
                  <span className="game-stat-label"> rozet</span>
                </div>
              </div>
            </div>
            {gamification.badges.length > 0 && (
              <div className="badges-row">
                {gamification.badges.slice(0, 4).map((b) => (
                  <span key={b.id} className="badge-icon" title={b.desc}>{b.icon}</span>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="sidebar-user">
          <Avatar name={currentUser.display_name || currentUser.username} size={36} />
          <div className="user-info">
            <strong>{currentUser.display_name || currentUser.username}</strong>
            <span>@{currentUser.username}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout} title="Çıkış Yap" aria-label="Çıkış Yap">⏻</button>
        </div>

        <div className="brand-competition">
          <div className="brand-comp-badge">TEKNOFEST 2026</div>
          <div className="brand-comp-title">NSosyal İnovasyon Yarışması</div>
          <div className="brand-comp-sub">Dijital Denge Platformu</div>
        </div>

        <div className="social-links">
          {SOCIAL_LINKS.map((s) => (
            <a key={s.label} href={s.url} target="_blank" rel="noopener noreferrer" className="social-link" title={s.label} aria-label={s.label}>
              {s.icon}
            </a>
          ))}
        </div>
      </aside>

        <main className="stage" id="main-content">
        <div className="mobile-header" style={{ display: "none" }}>
          <button className="mobile-menu-btn" onClick={() => setSidebarOpen(true)} aria-label="Menüyü aç">☰</button>
          <strong style={{ fontSize: 15 }}>Meridyen</strong>
          <button className="profile-btn" onClick={() => setPage("profil")} aria-label="Profil"><Avatar name={currentUser.display_name || currentUser.username} size={32} /></button>
        </div>

        <div className="topbar">
          <div className="topbar-left">
            <span className="presence-dot" />
            <span className="presence-text">Topluluğun için sakin bir alan</span>
          </div>
          <div className="topbar-right">
            <button type="button" className="topbar-btn" aria-label="Yapay Zekâ Asistanı" onClick={() => setShowAI(true)} title="Yapay Zekâ Asistanı">
              ✦
            </button>
            <div className="notif-wrapper">
              <button type="button" className={`topbar-btn${notifications.length ? " has-notification" : ""}`} aria-label="Bildirimler" onClick={() => setShowNotif(!showNotif)}>
                ⌁
                {notifications.length > 0 && <span className="notif-badge">{notifications.length}</span>}
              </button>
              {showNotif && (
                <div className="notif-panel">
                  <div className="notif-header">
                    <h4>Bildirimler</h4>
                    <div className="notif-header-actions">
                      <button
                        className={`notif-sound-toggle${notifSound ? " on" : ""}`}
                        onClick={() => {
                          const next = !notifSound;
                          setNotifSound(next);
                          try { localStorage.setItem("meridyen-notif-sound", next ? "on" : "off"); } catch {}
                        }}
                        title={notifSound ? "Sesi kapat" : "Sesi aç"}
                        aria-label={notifSound ? "Bildirim sesini kapat" : "Bildirim sesini aç"}
                      >
                        {notifSound ? "🔔" : "🔕"}
                      </button>
                      {notifications.length > 0 && (
                        <span className="notif-clear" onClick={() => setNotifications([])}>Temizle</span>
                      )}
                    </div>
                  </div>
                  {notifications.length === 0 ? (
                    <div className="notif-empty">
                      <div className="notif-empty-icon">🔔</div>
                      <p>Yeni bildirim yok</p>
                      <span>Bildirimler burada görünecek</span>
                    </div>
                  ) : (
                    notifications.map((n) => (
                      <div
                        key={n.id}
                        className={`notif-item${n.read ? " read" : ""}`}
                        onClick={() => {
                          setNotifications((prev) =>
                            prev.map((x) => x.id === n.id ? { ...x, read: true } : x)
                          );
                        }}
                      >
                        <div className={`notif-icon-box ${n.type}`}>
                          {n.type === "like" ? "♥" : n.type === "comment" ? "◇" : n.type === "follow" ? "◈" : "✦"}
                        </div>
                        <div className="notif-body">
                          <div className="notif-text" dangerouslySetInnerHTML={{ __html: n.text }} />
                          <span className="notif-time">{relativeTime(n.time)}</span>
                        </div>
                        {!n.read && <span className="notif-unread-dot" />}
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
            <button
              className="theme-toggle"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              aria-label={theme === "dark" ? "Aydınlık moda geç" : "Karanlık moda geç"}
              title={theme === "dark" ? "Aydınlık mod" : "Karanlık mod"}
            >
              {theme === "dark" ? "☀" : "☾"}
            </button>
            <Avatar name={currentUser.display_name || currentUser.username} size={32} />
          </div>
        </div>

        <header className="stage-header">
          <div className="stage-header-top">
            <div>
              <p className="eyebrow">Kişiselleştirilmiş deneyim</p>
              <h2 className="stage-title">
                {page === "akis" && "Akış"}
                {page === "denge" && "Denge raporu"}
                {page === "uretici" && "Üretici alanı"}
                {page === "profil" && "Profilim"}
                {page === "senaryolar" && "Kullanıcı Senaryoları"}
              </h2>
              <p className="stage-subtitle">
                {page === "akis" && "Modunu seç; içeriğin güvenliği, faydası ve tonu göre sıralansın."}
                {page === "denge" && "Dijital denge durumunu ve oturum istatistiklerini incele."}
                {page === "uretici" && "İçerik üreticileri için şeffaf gelir paylaşımı ve performans analitiği."}
                {page === "profil" && "Profil bilgilerin, rozetlerin ve sosyal medya bağlantıların."}
                {page === "senaryolar" && "Meridyen platformunun kullanıcı akışları ve senaryoları."}
              </p>
            </div>

            <fieldset className="mode-switch" aria-label="Kullanım modu">
              <legend>Kullanım modu</legend>
              {MODES.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  aria-pressed={mode === item.id}
                  className={`mode-chip${mode === item.id ? " on" : ""}`}
                  onClick={() => changeMode(item.id)}
                >
                  {item.label}
                </button>
              ))}
            </fieldset>
          </div>
          <p className="mode-hint" role="status">{currentMode?.hint}</p>
        </header>

        {message && (
          <div className="toast" role="status">
            <span>{message}</span>
            <button type="button" className="toast-close" onClick={() => setMessage("")} aria-label="Kapat">×</button>
          </div>
        )}

        {page === "akis" && <FeedView posts={posts} loading={loading} mode={mode} currentUser={currentUser} onPosted={load} onMessage={setMessage} onTip={setTipPost} onSubscribe={setSubPost} onReport={setReportPost} onToast={addToast} />}
        {page === "denge" && <BalanceView wellbeing={wellbeing} posts={posts} sessionMinutes={sessionMinutes} modeSwitches={modeSwitches} mode={mode} />}
        {page === "uretici" && <CreatorView creators={creators} currentUser={currentUser} mode={mode} onToast={addToast} />}
        {page === "profil" && <ProfileView gamification={gamification} currentUser={currentUser} />}
        {page === "senaryolar" && <ScenarioView />}

        <footer className="app-footer" role="contentinfo">
          <div className="footer-brand">Meridyen — Dijital Denge Platformu</div>
          <div className="footer-tagline">Güvenli, şeffaf ve kullanıcı odaklı sosyal medya deneyimi</div>
          <div className="footer-links">
            <span className="footer-link">Gizlilik Politikası</span>
            <span className="footer-link">Kullanım Koşulları</span>
            <span className="footer-link">Erişilebilirlik</span>
            <span className="footer-link" onClick={() => setShowShortcuts(true)} style={{ cursor: "pointer" }}>Klavye Kısayolları</span>
          </div>
          <div className="footer-badge">TEKNOFEST 2026 — NSosyal İnovasyon Yarışması</div>
        </footer>
      </main>

      {showAI && <AIAssistantModal onClose={() => setShowAI(false)} />}
      {tipPost && <TipModal post={tipPost} onClose={() => setTipPost(null)} onMessage={setMessage} />}
      {subPost && <SubscribeModal post={subPost} onClose={() => setSubPost(null)} onMessage={setMessage} />}
      {reportPost_ && <ReportModal post={reportPost_} onClose={() => setReportPost(null)} currentUser={currentUser} onToast={addToast} />}
      {showShortcuts && <ShortcutsModal onClose={() => setShowShortcuts(false)} />}
      {showOnboarding && <OnboardingModal onClose={() => { setShowOnboarding(false); try { localStorage.setItem("meridyen-onboarded", "1"); } catch {} }} />}

      <div className="toast-container" aria-live="polite" aria-label="Bildirimler">
        {toasts.map((t) => (
          <div key={t.id} className={`toast-item${t.exit ? " exit" : ""}`}>
            <span className={`toast-icon ${t.type}`}>{t.type === "success" ? "✓" : t.type === "error" ? "✕" : t.type === "warning" ? "⚠" : "ℹ"}</span>
            <span className="toast-text">{t.text}</span>
            <button className="toast-close" onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))} aria-label="Kapat">×</button>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   FEED VIEW
   ═══════════════════════════════════════════════════════════════════════════ */

function FeedView({ posts, loading, mode, currentUser, onPosted, onMessage, onTip, onSubscribe, onReport, onToast }) {
  const [feedPosts, setFeedPosts] = useState([]);
  const [feedLoading, setFeedLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("Tümü");
  const [sortBy, setSortBy] = useState("relevance");
  const [searchHistory, setSearchHistory] = useState(() => {
    try { return JSON.parse(localStorage.getItem("meridyen-search-history") || "[]"); } catch { return []; }
  });
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const observerRef = useRef();
  const pullStartRef = useRef(null);
  const feedContainerRef = useRef(null);
  const LIMIT = 10;

  const lastPostRef = useCallback((node) => {
    if (observerRef.current) observerRef.current.disconnect();
    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasMore && !loadingMore) {
        loadMore();
      }
    }, { threshold: 0.1 });
    if (node) observerRef.current.observe(node);
  }, [hasMore, loadingMore]);

  useEffect(() => {
    const h = setTimeout(() => setDebouncedQuery(searchQuery), 300);
    return () => clearTimeout(h);
  }, [searchQuery]);

  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setSearchResults(null);
      setShowSearchResults(false);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const res = await searchContent({ q: debouncedQuery, mode, limit: 20 });
        if (!cancelled) {
          setSearchResults(res);
          setShowSearchResults(true);
        }
      } catch {
        if (!cancelled) setSearchResults(null);
      }
    })();
    return () => { cancelled = true; };
  }, [debouncedQuery, mode]);

  async function loadFeed(p = 1, reset = false) {
    if (p === 1) {
      setFeedLoading(true);
    } else {
      setLoadingMore(true);
    }
    try {
      const data = await fetchFeed(mode, currentUser.username, { page: p, limit: LIMIT });
      const items = Array.isArray(data) ? data : (data.posts || []);
      if (reset || p === 1) {
        setFeedPosts(items);
      } else {
        setFeedPosts((prev) => [...prev, ...items]);
      }
      setHasMore(items.length === LIMIT);
      setPage(p);
    } catch {
      if (p === 1) onMessage("Akış yüklenemedi.");
    } finally {
      setFeedLoading(false);
      setLoadingMore(false);
    }
  }

  useEffect(() => { loadFeed(1, true); }, [mode, currentUser.username]);

  useEffect(() => {
    if (posts && posts.length > 0 && feedPosts.length === 0 && !feedLoading) {
      setFeedPosts(posts.slice(0, LIMIT));
      setHasMore(posts.length > LIMIT);
    }
  }, [posts]);

  async function loadMore() {
    if (!hasMore || loadingMore) return;
    await loadFeed(page + 1);
  }

  async function handleRefresh() {
    setIsRefreshing(true);
    setPullDistance(0);
    await loadFeed(1, true);
    setIsRefreshing(false);
  }

  function handleTouchStart(e) {
    if (window.scrollY === 0) {
      pullStartRef.current = e.touches[0].clientY;
    }
  }

  function handleTouchMove(e) {
    if (pullStartRef.current === null) return;
    const diff = e.touches[0].clientY - pullStartRef.current;
    if (diff > 0 && diff < 200) {
      setPullDistance(diff);
    }
  }

  function handleTouchEnd() {
    if (pullDistance > 80 && !isRefreshing) {
      handleRefresh();
    } else {
      setPullDistance(0);
    }
    pullStartRef.current = null;
  }

  function addToSearchHistory(q) {
    if (!q.trim()) return;
    const updated = [q, ...searchHistory.filter((s) => s !== q)].slice(0, 5);
    setSearchHistory(updated);
    try { localStorage.setItem("meridyen-search-history", JSON.stringify(updated)); } catch {}
  }

  function handleSearchSubmit(e) {
    e.preventDefault();
    if (searchQuery.trim()) addToSearchHistory(searchQuery.trim());
  }

  const displayPosts = showSearchResults && searchResults
    ? (searchResults.posts || [])
    : feedPosts;

  const sorted = [...displayPosts]
    .filter((p) => {
      if (activeCategory !== "Tümü" && p.category !== activeCategory) return false;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === "date") return new Date(b.created_at) - new Date(a.created_at);
      if (sortBy === "popular") return (b.like_count + b.comment_count) - (a.like_count + a.comment_count);
      const aFit = mode === "odak" ? a.focus_fit : mode === "ogrenme" ? a.learn_fit : a.fun_fit;
      const bFit = mode === "odak" ? b.focus_fit : mode === "ogrenme" ? b.learn_fit : b.fun_fit;
      return bFit - aFit;
    });

  return (
    <div
      className="layout-2col"
      ref={feedContainerRef}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <section>
        {pullDistance > 0 && (
          <div
            className="pull-refresh-indicator"
            style={{ height: Math.min(pullDistance, 80), opacity: Math.min(pullDistance / 80, 1) }}
          >
            <span className={`pull-refresh-spinner${isRefreshing || pullDistance > 80 ? " spinning" : ""}`}>
              ↻
            </span>
            <span>{isRefreshing ? "Yenileniyor…" : pullDistance > 80 ? "Bırakarak yenile" : "Aşağı çek"}</span>
          </div>
        )}

        <Composer mode={mode} currentUser={currentUser} onPosted={() => loadFeed(1, true)} onMessage={onMessage} />
        <div className="feed-header">
          <div className="feed-header-text">
            <h3>Önerilen içerikler</h3>
            <span>Yapay zekâ ile sıralanmış akış</span>
          </div>
          <div className="live-badge">
            <span className="live-badge-dot" />
            Güncelleme
          </div>
        </div>

        <form className="search-bar" onSubmit={handleSearchSubmit}>
          <div className="search-wrapper">
            <span className="search-icon">⌕</span>
            <input
              className="search-input"
              type="text"
              placeholder="İçerik veya kullanıcı ara…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Ara"
            />
            {searchQuery && (
              <button type="button" className="search-clear" onClick={() => { setSearchQuery(""); setShowSearchResults(false); setSearchResults(null); }} aria-label="Aramayı temizle">✕</button>
            )}
          </div>
          {!showSearchResults && searchHistory.length > 0 && searchQuery.length === 0 && (
            <div className="search-history">
              {searchHistory.map((h, i) => (
                <button key={i} className="search-history-item" type="button" onClick={() => setSearchQuery(h)}>
                  <span className="search-history-icon">◷</span> {h}
                </button>
              ))}
            </div>
          )}
        </form>

        {showSearchResults && searchResults && (
          <div className="search-results-info">
            <span>{searchResults.total ?? sorted.length} sonuç bulundu</span>
            <button className="search-results-close" onClick={() => { setShowSearchResults(false); setSearchResults(null); setSearchQuery(""); }}>Aramayı kapat</button>
          </div>
        )}

        <div className="feed-controls">
          <div className="filter-chips">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                className={`filter-chip${activeCategory === cat ? " active" : ""}`}
                onClick={() => setActiveCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
          <select className="sort-select" value={sortBy} onChange={(e) => setSortBy(e.target.value)} aria-label="Sıralama">
            <option value="relevance">Uyuma göre</option>
            <option value="date">Tarihe göre</option>
            <option value="popular">Popülerliğe göre</option>
          </select>
        </div>

        {feedLoading ? (
          <div className="feed-list">
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton skeleton-card">
                <div className="skeleton-header">
                  <div className="skeleton skeleton-avatar" />
                  <div className="skeleton-lines">
                    <div className="skeleton-line w60" />
                    <div className="skeleton-line w40" />
                  </div>
                </div>
                <div className="skeleton skeleton-body w80" />
                <div className="skeleton skeleton-body w100" />
                <div className="skeleton skeleton-body w60" />
              </div>
            ))}
          </div>
        ) : sorted.length === 0 ? (
          <div className="empty-state">
            <p>🔍</p>
            <p>{searchQuery || activeCategory !== "Tümü" ? "Aramanıza uygun içerik bulunamadı." : "Henüz içerik yok."}</p>
          </div>
        ) : (
          <div className="feed-list">
            {sorted.map((post, i) => {
              const isLast = i === sorted.length - 1;
              return (
                <div key={`${post.id}-${mode}`} ref={isLast ? lastPostRef : undefined}>
                  <PostCard
                    post={post}
                    rank={i + 1}
                    mode={mode}
                    currentUser={currentUser}
                    onMessage={onMessage}
                    onTip={onTip}
                    onSubscribe={onSubscribe}
                    onReport={onReport}
                    onToast={onToast}
                    onHashtagClick={(tag) => { setActiveCategory("Tümü"); setSearchQuery(`#${tag}`); }}
                    onRefresh={() => loadFeed(1, true)}
                  />
                </div>
              );
            })}
            {loadingMore && (
              <div className="feed-loading-more">
                <span className="spinner-sm" /> Daha fazla yükleniyor…
              </div>
            )}
            {!hasMore && sorted.length > 0 && (
              <div className="feed-end">Tüm içerikler yüklendi</div>
            )}
          </div>
        )}
      </section>

      <aside className="side-stack">
        <TrendingSidebar mode={mode} />
        <div className="panel">
          <h3 className="panel-title">Nasıl çalışır?</h3>
          <ul className="panel-list">
            <li>Seçtiğin mod, akışını biçimlendirir.</li>
            <li>Güvenlik ve fayda öncelikli sıralama.</li>
            <li>Her önerinin gerekçesi şeffaf.</li>
          </ul>
        </div>
        <div className="panel">
          <h3 className="panel-title">Gizlilik ilkesi</h3>
          <ul className="panel-list">
            <li>Duygu tahmini yapılmaz; kontrol sende.</li>
            <li>Verilerin yalnızca senin deneyimini iyileştirir.</li>
            <li>İçerik tercihlerin üçüncü kişilerle paylaşılmaz.</li>
          </ul>
        </div>
      </aside>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   COMPOSER
   ═══════════════════════════════════════════════════════════════════════════ */

function Composer({ mode, currentUser, onPosted, onMessage }) {
  const [text, setText] = useState("");
  const [category, setCategory] = useState("Eğitim");
  const [preview, setPreview] = useState(null);
  const [busy, setBusy] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);

  async function onImageSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      onMessage("Fotoğraf boyutu 5MB'dan küçük olmalı.");
      return;
    }
    const compressed = await compressImage(file);
    setImagePreview(compressed);
  }

  function removeImage() {
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  useEffect(() => {
    if (text.trim().length < 8) { setPreview(null); return undefined; }
    const h = window.setTimeout(async () => {
      try {
        setPreview(await previewAnalysis({ title: text.slice(0, 80), description: text, category, mode }));
      } catch { setPreview(null); }
    }, 350);
    return () => window.clearTimeout(h);
  }, [text, category, mode]);

  async function publish() {
    if (!text.trim() && !imagePreview) return;
    setBusy(true);
    try {
      const created = await createPost({
        author_username: currentUser.username,
        display_name: currentUser.display_name || currentUser.username,
        content: text || "Fotoğraf paylaşımı",
        category,
        image_url: imagePreview || null,
      });
      setText("");
      removeImage();
      onPosted();
      onMessage(created.is_publishable ? "İçerik yayınlandı." : "İçerik alındı; güvenlik filtresi nedeniyle görünürlüğü kısıtlandı.");
    } catch (e) {
      onMessage(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel composer">
      <div className="composer-glow" />
      <label htmlFor="composer-input">Düşüncelerini paylaş</label>
      <textarea
        id="composer-input"
        value={text}
        maxLength={500}
        onChange={(e) => setText(e.target.value)}
        placeholder="Bir fikir, keşif ya da kısa bir not bırak…"
      />
      {imagePreview && (
        <div className="composer-image-preview">
          <img src={imagePreview} alt="Önizleme" />
          <button type="button" className="composer-image-remove" onClick={removeImage} aria-label="Fotoğrafı kaldır">×</button>
        </div>
      )}
      {imagePreview && <div className="compress-badge">⚡ Fotoğraf otomatik sıkıştırıldı</div>}
      <div className="composer-toolbar">
        <select className="composer-select" value={category} onChange={(e) => setCategory(e.target.value)} aria-label="Kategori">
          {["Eğitim", "Teknoloji", "Bilim", "Sanat", "Spor", "Genel"].map((c) => <option key={c}>{c}</option>)}
        </select>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="visually-hidden"
          onChange={onImageSelect}
          aria-label="Fotoğraf seç"
        />
        <button type="button" className="composer-image-btn" onClick={() => fileInputRef.current?.click()} title="Fotoğraf ekle">
          📷
        </button>
        <span className="composer-count">{text.length}/500</span>
        <button type="button" className="btn-primary" disabled={(!text.trim() && !imagePreview) || busy} onClick={publish}>Paylaş</button>
      </div>
      {preview && (
        <div className="preview-row" aria-live="polite">
          <PreviewBadge label="Güvenlik" value={preview.analysis.safety_score} />
          <PreviewBadge label="Fayda" value={preview.analysis.wellbeing_score} />
          <PreviewBadge label="Sıralama" value={preview.ranking.rank_score} />
        </div>
      )}
    </section>
  );
}

function PreviewBadge({ label, value }) {
  const v = Number(value || 0);
  const cls = v < 40 ? "warn" : v < 65 ? "mid" : "ok";
  return <span className={`preview-badge ${cls}`}>{label} <strong>{Math.round(v)}</strong></span>;
}

/* ═══════════════════════════════════════════════════════════════════════════
   POST CARD
   ═══════════════════════════════════════════════════════════════════════════ */

function PostCard({ post, mode, currentUser, onMessage, onTip, onSubscribe, onReport, onToast, onHashtagClick, onRefresh }) {
  const [open, setOpen] = useState(false);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");
  const [liked, setLiked] = useState(post.liked_by_me);
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [bookmarked, setBookmarked] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState(post.content);
  const [editCategory, setEditCategory] = useState(post.category);
  const [deleting, setDeleting] = useState(false);

  const isAuthor = currentUser && (currentUser.username === post.author_username);

  async function onLike() {
    try {
      const r = await toggleLike(post.id, currentUser.username);
      setLiked(r.liked);
      setLikeCount(r.like_count);
    } catch (e) { onMessage(e.message); }
  }

  async function onBookmark() {
    try {
      const r = await toggleBookmark(post.id, currentUser.username);
      setBookmarked(r.bookmarked);
      onToast(r.bookmarked ? "İçerik kaydedildi." : "Kayıt kaldırıldı.", "success");
    } catch (e) { onMessage(e.message); }
  }

  async function onShare() {
    try {
      await navigator.clipboard.writeText(post.content);
      onToast("İçerik panoya kopyalandı.", "success");
    } catch {
      onToast("Kopyalanamadı.", "error");
    }
  }

  async function onToggleComments() {
    const next = !open;
    setOpen(next);
    if (next) {
      try { setComments(await fetchComments(post.id)); } catch (e) { onMessage(e.message); }
    }
  }

  async function sendComment() {
    if (!commentText.trim()) return;
    try {
      const c = await createComment(post.id, currentUser.username, commentText);
      setComments((cur) => [...cur, c]);
      setCommentText("");
    } catch (e) { onMessage(e.message); }
  }

  async function saveEdit() {
    if (!editContent.trim()) return;
    try {
      await editPost(post.id, { content: editContent, category: editCategory });
      setEditing(false);
      post.content = editContent;
      post.category = editCategory;
      onToast("İçerik güncellendi.", "success");
      if (onRefresh) onRefresh();
    } catch (e) { onToast(e.message, "error"); }
  }

  async function confirmDelete() {
    try {
      await deletePost(post.id, currentUser.username);
      setDeleting(false);
      onToast("İçerik silindi.", "success");
      if (onRefresh) onRefresh();
    } catch (e) { onToast(e.message, "error"); }
  }

  function parseContent(text) {
    if (!text) return text;
    const parts = [];
    const regex = /(#[a-zA-ZçğıöşüÇĞIİÖŞÜ0-9_]+)|(@[a-zA-ZçğıöşüÇĞIİÖŞÜ0-9_]+)/g;
    let lastIndex = 0;
    let match;
    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }
      if (match[1]) {
        const tag = match[1].slice(1);
        parts.push(
          <span key={match.index} className="hashtag" onClick={(e) => { e.stopPropagation(); if (onHashtagClick) onHashtagClick(tag); }}>
            #{tag}
          </span>
        );
      } else if (match[2]) {
        const uname = match[2].slice(1);
        parts.push(
          <span key={match.index} className="mention">
            @{uname}
          </span>
        );
      }
      lastIndex = regex.lastIndex;
    }
    if (lastIndex < text.length) parts.push(text.slice(lastIndex));
    return parts;
  }

  const hashtags = (post.content || "").match(/#[a-zA-ZçğıöşüÇĞIİÖŞÜ0-9_]+/g) || [];

  const modeFit = mode === "odak" ? post.focus_fit : mode === "ogrenme" ? post.learn_fit : post.fun_fit;

  return (
    <article className={`post-card${post.is_publishable ? "" : " dimmed"}`}>
      <div className="post-body">
        <div className="post-header">
          <Avatar name={post.display_name} size={36} />
          <div className="post-meta">
            <span className="post-author">{post.display_name}</span>
            <span className="post-details">@{post.author_username} · {formatTime(post.created_at)} · {post.category}</span>
          </div>
          <div className="fit-badge">
            <span className="fit-number">{Math.round(modeFit)}</span>
            <span className="fit-label">uyum</span>
          </div>
          {isAuthor && !editing && (
            <div className="post-author-actions">
              <button type="button" className="post-author-btn" onClick={() => setEditing(true)} title="Düzenle" aria-label="Gönderiyi düzenle">
                ✎
              </button>
              <button type="button" className="post-author-btn danger" onClick={() => setDeleting(true)} title="Sil" aria-label="Gönderiyi sil">
                🗑
              </button>
            </div>
          )}
        </div>
        {editing ? (
          <div className="post-edit-area">
            <textarea
              className="post-edit-textarea"
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              maxLength={500}
              rows={4}
            />
            <div className="post-edit-toolbar">
              <select className="composer-select" value={editCategory} onChange={(e) => setEditCategory(e.target.value)}>
                {["Eğitim", "Teknoloji", "Bilim", "Sanat", "Spor", "Genel"].map((c) => <option key={c}>{c}</option>)}
              </select>
              <div className="post-edit-actions">
                <button type="button" className="btn-small" onClick={() => { setEditing(false); setEditContent(post.content); setEditCategory(post.category); }}>İptal</button>
                <button type="button" className="btn-primary btn-small" onClick={saveEdit}>Kaydet</button>
              </div>
            </div>
          </div>
        ) : (
          <p className="post-content">{parseContent(post.content)}</p>
        )}
        {post.image_url && (
          <div className="post-image">
            <img src={post.image_url} alt="Paylaşım görseli" loading="lazy" />
          </div>
        )}
        {post.moderation_note && <div className="post-warning">{post.moderation_note}</div>}
        <dl className="score-chips">
          <div className="score-chip">
            <dt className="chip-label">Denge</dt>
            <dd className="chip-content">
              <span className="chip-bar-track"><span className="chip-bar-fill" style={{ width: `${Math.min(post.wellbeing_score, 100)}%` }} /></span>
              <span className="chip-value">{Math.round(post.wellbeing_score)}</span>
            </dd>
          </div>
          <div className="score-chip">
            <dt className="chip-label">Güvenlik</dt>
            <dd className="chip-content">
              <span className="chip-bar-track"><span className="chip-bar-fill" style={{ width: `${Math.min(post.safety_score, 100)}%` }} /></span>
              <span className="chip-value">{Math.round(post.safety_score)}</span>
            </dd>
          </div>
          <div className="score-chip">
            <dt className="chip-label">Erişim</dt>
            <dd className="chip-content">
              <span className="chip-value">×{post.visibility_multiplier.toFixed(1)}</span>
            </dd>
          </div>
        </dl>
        <details className="reasons-toggle">
          <summary>Neden önerildi?</summary>
          <ul className="reasons-list">
            {post.rank_reasons.map((r) => <li key={r}>{r}</li>)}
          </ul>
        </details>
        {hashtags.length > 0 && (
          <div className="post-hashtags">
            {hashtags.map((h, i) => (
              <span key={i} className="hashtag" onClick={(e) => { e.stopPropagation(); if (onHashtagClick) onHashtagClick(h.slice(1)); }}>{h}</span>
            ))}
          </div>
        )}
      </div>
      <div className="post-actions">
        <button type="button" aria-pressed={liked} className={`action-btn${liked ? " liked" : ""}`} onClick={onLike}>
          <span className="action-icon">{liked ? "♥" : "♡"}</span> {likeCount}
        </button>
        <button type="button" className="action-btn" onClick={onToggleComments}>
          <span className="action-icon">◇</span> {post.comment_count}
        </button>
        <button type="button" className={`action-btn${bookmarked ? " bookmarked" : ""}`} onClick={onBookmark} title="Kaydet">
          <span className="action-icon">{bookmarked ? "◆" : "◇"}</span> Kaydet
        </button>
        <button type="button" className="action-btn" onClick={onShare} title="Paylaş">
          <span className="action-icon">↗</span> Paylaş
        </button>
        <span className="action-spacer" />
        <button type="button" className="action-btn tip-btn" onClick={() => onTip(post)} title="Bahşiş gönder">
          <span className="action-icon">⟐</span> Bahşiş
        </button>
        <button type="button" className="action-btn subscribe-btn" onClick={() => onSubscribe(post)} title="Abone ol">
          <span className="action-icon">★</span> Abone
        </button>
        {onReport && (
          <button type="button" className="action-btn" onClick={() => onReport(post)} title="Raporla" style={{ fontSize: 11, color: "var(--text-tertiary)" }}>
            ⚠
          </button>
        )}
      </div>
      {open && (
        <div className="comments-section">
          {comments.length === 0 && <div className="comments-empty">Henüz yorum yok</div>}
          {comments.map((c) => (
            <div key={c.id} className="comment-item">
              <strong>@{c.username}</strong>
              <span>{c.content}</span>
            </div>
          ))}
          <div className="comment-form">
            <input className="comment-input" value={commentText} onChange={(e) => setCommentText(e.target.value)} placeholder="Yorum ekle" aria-label="Yorum" />
            <button type="button" className="btn-small" onClick={sendComment}>Gönder</button>
          </div>
        </div>
      )}
      {deleting && (
        <div className="modal-overlay" onClick={() => setDeleting(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 380 }}>
            <div className="modal-header">
              <h3>Gönderiyi Sil</h3>
              <button className="modal-close" onClick={() => setDeleting(false)} aria-label="Kapat">×</button>
            </div>
            <div className="modal-body">
              <p className="panel-text">Bu gönderiyi silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.</p>
            </div>
            <div className="modal-footer">
              <button className="btn-small" onClick={() => setDeleting(false)}>İptal</button>
              <button className="btn-danger" onClick={confirmDelete}>Evet, Sil</button>
            </div>
          </div>
        </div>
      )}
    </article>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   BALANCE VIEW
   ═══════════════════════════════════════════════════════════════════════════ */

function BalanceView({ wellbeing, posts, sessionMinutes, modeSwitches, mode }) {
  const top = posts.slice(0, 3);
  const toxicShare = posts.length ? Math.round((posts.filter((p) => p.safety_score < 70).length / posts.length) * 100) : 0;

  return (
    <div className="stat-grid">
      <article className="stat-card">
        <span className="stat-card-label">Ortalama denge</span>
        <strong className="stat-card-value">{wellbeing?.avg_wellbeing ?? 0}</strong>
      </article>
      <article className="stat-card">
        <span className="stat-card-label">Güvenli içerik</span>
        <strong className="stat-card-value">%{wellbeing?.safe_ratio ?? 0}</strong>
      </article>
      <article className="stat-card">
        <span className="stat-card-label">Oturum</span>
        <strong className="stat-card-value">{sessionMinutes || "<1"} dk</strong>
      </article>
      <article className="stat-card">
        <span className="stat-card-label">Mod değişimi</span>
        <strong className="stat-card-value">{modeSwitches}</strong>
      </article>
      <article className="stat-card span-2">
        <h3 className="panel-title">Bu modda öne çıkanlar</h3>
        <p className="panel-text">
          Aktif mod: <strong>{mode}</strong> · Düşük güvenli içerik oranı %{toxicShare}.
        </p>
        <ol>
          {top.map((p) => (
            <li key={p.id}>{p.display_name} — {p.rank_score.toFixed(1)} · denge {Math.round(p.wellbeing_score)}</li>
          ))}
        </ol>
      </article>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   CREATOR VIEW
   ═══════════════════════════════════════════════════════════════════════════ */

function CreatorView({ creators, currentUser, onToast }) {
  return (
    <div>
      <CreatorAnalytics creators={creators} currentUser={currentUser} mode="odak" onToast={onToast} />

      <div className="revenue-panel">
        <div className="revenue-header">
          <h3>Haftalık gelir havuzu</h3>
          <span className="revenue-badge">Gerçek zamanlı</span>
        </div>
        <p className="panel-text">
          Pay, görünürlük çarpanı ve refah skoruna göre dağıtılır. Kaliteli ve güvenli içerik daha fazla görünürlük kazanır.
        </p>
        <table className="data-table">
          <thead>
            <tr>
              <th>Üretici</th>
              <th>Refah</th>
              <th>Çarpan</th>
              <th>Pay</th>
            </tr>
          </thead>
          <tbody>
            {creators.map((c) => (
              <tr key={c.author_username} className={c.author_username === currentUser.username ? "is-me" : undefined}>
                <td>{c.display_name}</td>
                <td>{c.avg_wellbeing}</td>
                <td>×{c.avg_multiplier.toFixed(2)}</td>
                <td>{c.estimated_weekly_share} TL</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   PROFILE VIEW
   ═══════════════════════════════════════════════════════════════════════════ */

function ProfileView({ gamification, currentUser }) {
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState(currentUser.display_name || "");
  const [editBio, setEditBio] = useState(currentUser.bio || "");
  const [editCategory, setEditCategory] = useState(currentUser.category || "Genel");
  const [saving, setSaving] = useState(false);

  async function saveProfile() {
    if (!editName.trim()) return;
    setSaving(true);
    try {
      await updateProfile({
        display_name: editName.trim(),
        bio: editBio.trim(),
        category: editCategory,
      });
      const updated = { ...currentUser, display_name: editName.trim(), bio: editBio.trim(), category: editCategory };
      localStorage.setItem("meridyen-user", JSON.stringify(updated));
      setEditing(false);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="profile-hero">
        <Avatar name={currentUser.display_name || currentUser.username} size={80} />
        <div className="profile-info">
          <h2>{currentUser.display_name || currentUser.username}</h2>
          <p className="profile-handle">@{currentUser.username}</p>
          <p className="profile-bio">{currentUser.bio || "Meridyen platformunda dijital dengeyi keşfeden, içerik üreten ve toplulukla bağlantı kuran bir kullanıcı."}</p>
          <div className="profile-stats-row">
            <div className="profile-stat">
              <span className="profile-stat-num">142</span>
              <span className="profile-stat-label">Gönderi</span>
            </div>
            <div className="profile-stat">
              <span className="profile-stat-num">3.2K</span>
              <span className="profile-stat-label">Beğeni</span>
            </div>
            <div className="profile-stat">
              <span className="profile-stat-num">89</span>
              <span className="profile-stat-label">Takipçi</span>
            </div>
            <div className="profile-stat">
              <span className="profile-stat-num">67</span>
              <span className="profile-stat-label">Takip</span>
            </div>
          </div>
          <button type="button" className="btn-primary btn-small" onClick={() => setEditing(true)}>
            ✎ Profili Düzenle
          </button>
        </div>
      </div>

      <div className="profile-grid">
        {gamification && (
          <div className="panel">
            <h3 className="panel-title">Oyunlaştırma</h3>
            <p className="panel-text">
              Seviye: <strong>{gamification.level}</strong> · {gamification.xp}/{gamification.xp_for_next} XP
            </p>
            <div className="progress-track" style={{ marginTop: 10 }}>
              <div className="progress-fill" style={{ width: `${(gamification.xp / gamification.xp_for_next) * 100}%` }} />
            </div>
            <div className="game-stats" style={{ marginTop: 12 }}>
              <div className="game-stat-item">
                <span className="game-stat-icon">△</span>
                <div>
                  <span className="game-stat-value">{gamification.streak}</span>
                  <span className="game-stat-label"> gün streak</span>
                </div>
              </div>
              <div className="game-stat-item">
                <span className="game-stat-icon">✦</span>
                <div>
                  <span className="game-stat-value">{gamification.badge_count}</span>
                  <span className="game-stat-label"> rozet</span>
                </div>
              </div>
            </div>
            {gamification.badges.length > 0 && (
              <div className="badges-row" style={{ marginTop: 10 }}>
                {gamification.badges.map((b) => (
                  <span key={b.id} className="badge-icon" title={b.desc}>{b.icon}</span>
                ))}
              </div>
            )}
          </div>
        )}
        <div className="panel">
          <h3 className="panel-title">Sosyal medya</h3>
          <ul className="panel-list">
            {SOCIAL_LINKS.map((s) => (
              <li key={s.label}>
                <a href={s.url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent)" }}>
                  {s.icon} {s.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {editing && (
        <div className="modal-overlay" onClick={() => setEditing(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 420 }}>
            <div className="modal-header">
              <h3>Profili Düzenle</h3>
              <button className="modal-close" onClick={() => setEditing(false)} aria-label="Kapat">×</button>
            </div>
            <div className="modal-body">
              <div className="auth-field">
                <label className="auth-label" htmlFor="edit-display-name">Görünen Ad</label>
                <input
                  id="edit-display-name"
                  className="auth-input"
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  maxLength={50}
                />
              </div>
              <div className="auth-field">
                <label className="auth-label" htmlFor="edit-bio">Biyografi</label>
                <input
                  id="edit-bio"
                  className="auth-input"
                  type="text"
                  value={editBio}
                  onChange={(e) => setEditBio(e.target.value)}
                  placeholder="Kendinden kısaca bahset…"
                  maxLength={200}
                />
              </div>
              <div className="auth-field">
                <label className="auth-label" htmlFor="edit-category">İlgi Alanı</label>
                <select
                  id="edit-category"
                  className="auth-select"
                  value={editCategory}
                  onChange={(e) => setEditCategory(e.target.value)}
                >
                  {CATEGORIES.filter((c) => c !== "Tümü").map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-small" onClick={() => setEditing(false)}>İptal</button>
              <button className="btn-primary" disabled={saving || !editName.trim()} onClick={saveProfile}>
                {saving ? "Kaydediliyor…" : "Kaydet"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   AI ASSISTANT MODAL
   ═══════════════════════════════════════════════════════════════════════════ */

function AIAssistantModal({ onClose }) {
  const [messages, setMessages] = useState([
    { role: "ai", text: "Merhaba! Ben Meridyen Yapay Zekâ Asistanı. İçeriklerini analiz etmek, öneriler almak veya platform hakkında bilgi edinmek için bana bir şey sor." },
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [messages, thinking]);

  async function send(text) {
    const q = (text || input).trim();
    if (!q || thinking) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setThinking(true);
    try {
      const reply = await aiAssistant(q);
      setMessages((prev) => [...prev, { role: "ai", text: reply }]);
    } catch {
      setMessages((prev) => [...prev, { role: "ai", text: "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin." }]);
    } finally {
      setThinking(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal ai-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3><span className="ai-sparkle">✦</span> Yapay Zekâ Asistanı</h3>
          <button className="modal-close" onClick={onClose} aria-label="Kapat">×</button>
        </div>
        <div className="ai-chat" ref={chatRef}>
          {messages.map((m, i) => (
            <div key={i} className={`ai-msg ai-msg-${m.role}`}>
              {m.role === "ai" && <span className="ai-msg-avatar">✦</span>}
              <div className={`ai-bubble ai-bubble-${m.role}`}>
                {m.text.split("\n").map((line, j) => <p key={j}>{line}</p>)}
              </div>
            </div>
          ))}
          {thinking && (
            <div className="ai-msg ai-msg-ai">
              <span className="ai-msg-avatar">✦</span>
              <div className="ai-bubble ai-bubble-ai ai-thinking">
                <span className="dot" /><span className="dot" /><span className="dot" />
              </div>
            </div>
          )}
        </div>
        <div className="ai-suggestions">
          {AI_SUGGESTIONS.map((s, i) => (
            <button key={i} className="ai-chip" onClick={() => send(s.text.replace(/[✦◈△◐] /, ""))}>
              <span className="ai-chip-icon">{s.icon}</span> {s.text.replace(/[✦◈△◐] /, "")}
            </button>
          ))}
        </div>
        <div className="modal-footer">
          <div className="ai-input-row">
            <input
              className="ai-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Yapay zekâya bir şey sor…"
              aria-label="AI isteği"
            />
            <button className="btn-primary" type="button" onClick={() => send()} disabled={thinking || !input.trim()}>
              Gönder
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   TIP MODAL
   ═══════════════════════════════════════════════════════════════════════════ */

function TipModal({ post, onClose, onMessage }) {
  const [selected, setSelected] = useState(null);

  function send() {
    if (!selected) return;
    onMessage(`${selected}₺ bahşiş gönderildi! Teşekkürler.`);
    onClose();
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 400 }}>
        <div className="modal-header">
          <h3>⟐ Bahşiş Gönder</h3>
          <button className="modal-close" onClick={onClose} aria-label="Kapat">×</button>
        </div>
        <div className="modal-body">
          <p className="panel-text">
            <strong>{post.display_name}</strong> için bir bahşiş miktarı seç.
          </p>
          <div className="tip-grid">
            {TIP_OPTIONS.map((t) => (
              <button
                key={t.amount}
                className={`tip-option${selected === t.amount ? " selected" : ""}`}
                onClick={() => setSelected(t.amount)}
              >
                <span className="tip-amount">{t.amount}₺</span>
                <span className="tip-label">{t.label}</span>
              </button>
            ))}
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn-primary" disabled={!selected} onClick={send} style={{ width: "100%", justifyContent: "center" }}>
            Gönder
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   SUBSCRIBE MODAL
   ═══════════════════════════════════════════════════════════════════════════ */

function SubscribeModal({ post, onClose, onMessage }) {
  function subscribe(tier) {
    onMessage(`${tier.name} planına abone oldun! Hoş geldin.`);
    onClose();
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 420 }}>
        <div className="modal-header">
          <h3>★ Premium Abonelik</h3>
          <button className="modal-close" onClick={onClose} aria-label="Kapat">×</button>
        </div>
        <div className="modal-body">
          <p className="panel-text">
            <strong>{post.display_name}</strong> için bir abonelik planı seç.
          </p>
          <div className="tier-list">
            {SUB_TIERS.map((t) => (
              <button key={t.name} className="tier-card" onClick={() => subscribe(t)}>
                <div>
                  <div className="tier-name">{t.name}</div>
                  <div className="tier-desc">{t.desc}</div>
                </div>
                <div className="tier-price">{t.price}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   ONBOARDING MODAL
   ═══════════════════════════════════════════════════════════════════════════ */

function OnboardingModal({ onClose }) {
  const [step, setStep] = useState(0);
  const s = ONBOARDING_STEPS[step];
  const isLast = step === ONBOARDING_STEPS.length - 1;

  return (
    <div className="onboarding-overlay" role="dialog" aria-label="Hoş geldin">
      <div className="onboarding-card">
        <div className="onboarding-visual">{s.icon}</div>
        <div className="onboarding-body">
          <h2>{s.title}</h2>
          <p>{s.text}</p>
        </div>
        <div className="onboarding-dots">
          {ONBOARDING_STEPS.map((_, i) => (
            <div key={i} className={`onboarding-dot${i === step ? " active" : ""}`} />
          ))}
        </div>
        <div className="onboarding-footer">
          <button className="onboarding-skip" onClick={onClose}>Atla</button>
          <button className="btn-primary" onClick={() => isLast ? onClose() : setStep(step + 1)}>
            {isLast ? "Başla" : "İleri"}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   REPORT MODAL
   ═══════════════════════════════════════════════════════════════════════════ */

function ReportModal({ post, onClose, currentUser, onToast }) {
  const [selected, setSelected] = useState(null);
  const [sent, setSent] = useState(false);

  async function submit() {
    if (!selected) return;
    try {
      await reportPost(post.id, currentUser.username, selected);
      setSent(true);
      onToast("İçerik raporlandı. Teşekkürler.", "success");
    } catch {
      onToast("Rapor gönderilemedi.", "error");
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 420 }}>
        <div className="modal-header">
          <h3>⚠ İçerik Raporla</h3>
          <button className="modal-close" onClick={onClose} aria-label="Kapat">×</button>
        </div>
        <div className="modal-body">
          {sent ? (
            <div className="empty-state" style={{ padding: "24px 0" }}>
              <div className="empty-state-icon">✓</div>
              <h3>Raporun alındı</h3>
              <p>İnceleme sürecinden sonra gerekli işlem yapılacaktır.</p>
            </div>
          ) : (
            <>
              <p className="panel-text" style={{ marginBottom: 12 }}>
                <strong>{post.display_name}</strong> tarafından paylaşılan içerik neden raporlanıyor?
              </p>
              <div className="report-options">
                {REPORT_REASONS.map((r) => (
                  <button
                    key={r}
                    className={`report-option${selected === r ? " selected" : ""}`}
                    onClick={() => setSelected(r)}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
        {!sent && (
          <div className="modal-footer">
            <button className="btn-primary" disabled={!selected} onClick={submit} style={{ width: "100%", justifyContent: "center" }}>
              Raporu Gönder
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   KEYBOARD SHORTCUTS MODAL
   ═══════════════════════════════════════════════════════════════════════════ */

function ShortcutsModal({ onClose }) {
  const shortcuts = [
    { keys: ["D", "T"], desc: "Karanlık/aydınlık mod değiştir" },
    { keys: ["1"], desc: "Akış sayfası" },
    { keys: ["2"], desc: "Denge sayfası" },
    { keys: ["3"], desc: "Üretici sayfası" },
    { keys: ["4"], desc: "Profil sayfası" },
    { keys: ["A"], desc: "Yapay Zekâ Asistanı" },
    { keys: ["Esc"], desc: "Paneli / menüyü kapat" },
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 400 }}>
        <div className="modal-header">
          <h3>⌨ Klavye Kısayolları</h3>
          <button className="modal-close" onClick={onClose} aria-label="Kapat">×</button>
        </div>
        <div className="modal-body">
          <div className="shortcuts-list">
            {shortcuts.map((s) => (
              <div key={s.desc} className="shortcut-row">
                <span className="shortcut-desc">{s.desc}</span>
                <div className="shortcut-keys">
                  {s.keys.map((k) => <kbd key={k}>{k}</kbd>)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   SCENARIO VIEW
   ═══════════════════════════════════════════════════════════════════════════ */

function ScenarioView() {
  return (
    <div>
      <p className="panel-text" style={{ marginBottom: 16 }}>
        Aşağıda Meridyen platformunun temel kullanıcı akışları ve senaryoları yer almaktadır.
      </p>
      <div className="scenario-grid">
        {SCENARIOS.map((s) => (
          <div key={s.step} className="scenario-card">
            <div className="scenario-step">{s.step}</div>
            <h4>{s.title}</h4>
            <p>{s.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   TRENDING SIDEBAR
   ═══════════════════════════════════════════════════════════════════════════ */

function TrendingSidebar({ mode }) {
  const [trending, setTrending] = useState([]);

  useEffect(() => {
    fetchTrending(mode).then(setTrending).catch(() => {});
  }, [mode]);

  if (trending.length === 0) return null;

  return (
    <div className="panel">
      <h3 className="panel-title">🔥 Popüler İçerikler</h3>
      <ul className="trending-list">
        {trending.slice(0, 5).map((p, i) => (
          <li key={p.id} className="trending-item">
            <span className={`trending-rank${i === 0 ? " top" : ""}`}>{i + 1}</span>
            <div className="trending-info">
              <div className="trending-title">{p.content.slice(0, 40)}…</div>
              <div className="trending-meta">{p.display_name} · {p.category}</div>
            </div>
            <span className="trending-score">{Math.round(p.rank_score)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════════════
   CREATOR ANALYTICS (Enhanced)
   ═══════════════════════════════════════════════════════════════════════════ */

function CreatorAnalytics({ creators, currentUser, mode, onToast }) {
  const mine = creators.find((c) => c.author_username === currentUser.username);
  const days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];
  const [chartLoading, setChartLoading] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setChartLoading(false), 300);
    return () => clearTimeout(t);
  }, []);

  const weeklyWellbeing = days.map((d, i) => ({
    name: d,
    denge: mine ? Math.round(mine.avg_wellbeing * (0.6 + (i * 0.08) + (((i * 7 + 3) % 5) * 0.05))) : Math.round(30 + i * 5 + ((i * 3) % 7)),
  }));

  const categoryData = [
    { name: "Eğitim", value: 35, color: CHART_COLORS.primary },
    { name: "Teknoloji", value: 25, color: CHART_COLORS.purple },
    { name: "Bilim", value: 18, color: CHART_COLORS.success },
    { name: "Sanat", value: 12, color: CHART_COLORS.pink },
    { name: "Spor", value: 10, color: CHART_COLORS.accent },
  ];

  const engagementData = days.map((d, i) => ({
    name: d,
    begeni: Math.round(10 + Math.random() * 30 + i * 2),
    yorum: Math.round(3 + Math.random() * 15 + i),
  }));

  const fitData = creators.slice(0, 5).map((c) => ({
    name: c.display_name?.slice(0, 8) || "—",
    odak: Math.round(c.avg_wellbeing * 1.1),
    ogrenme: Math.round(c.avg_wellbeing * 0.9),
    eglence: Math.round(c.avg_wellbeing * 0.75),
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;
    return (
      <div className="chart-tooltip">
        <p className="chart-tooltip-label">{label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color }}>{p.name}: {p.value}</p>
        ))}
      </div>
    );
  };

  return (
    <div>
      <div className="analytics-grid">
        <div className="analytics-card">
          <div className="analytics-card-label">Haftalık Gelir</div>
          <div className="analytics-card-value">{mine ? `${mine.estimated_weekly_share}₺` : "0₺"}</div>
          <div className="analytics-card-change up">↑ Bu hafta</div>
        </div>
        <div className="analytics-card">
          <div className="analytics-card-label">Ort. Refah</div>
          <div className="analytics-card-value">{mine ? mine.avg_wellbeing : "—"}</div>
        </div>
        <div className="analytics-card">
          <div className="analytics-card-label">Görünürlük</div>
          <div className="analytics-card-value">{mine ? `×${mine.avg_multiplier.toFixed(2)}` : "—"}</div>
        </div>
        <div className="analytics-card">
          <div className="analytics-card-label">İçerik Sayısı</div>
          <div className="analytics-card-value">{mine ? mine.post_count : 0}</div>
        </div>
      </div>

      {chartLoading ? (
        <div className="chart-loading-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton skeleton-card" style={{ height: 220 }} />
          ))}
        </div>
      ) : (
        <div className="charts-grid">
          <div className="panel chart-panel">
            <h3 className="panel-title">Haftalık Refah Grafiği</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={weeklyWellbeing} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="gradWellbeing" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: "var(--text-tertiary)" }} />
                  <YAxis tick={{ fontSize: 11, fill: "var(--text-tertiary)" }} />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="denge" stroke={CHART_COLORS.primary} fill="url(#gradWellbeing)" strokeWidth={2} name="Denge" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel chart-panel">
            <h3 className="panel-title">Kategori Dağılımı</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ name, percent }) => `${name} %${(percent * 100).toFixed(0)}`}
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel chart-panel">
            <h3 className="panel-title">Etkileşim Zaman Çizelgesi</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={engagementData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: "var(--text-tertiary)" }} />
                  <YAxis tick={{ fontSize: 11, fill: "var(--text-tertiary)" }} />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="begeni" stroke={CHART_COLORS.danger} strokeWidth={2} dot={{ r: 3 }} name="Beğeni" />
                  <Line type="monotone" dataKey="yorum" stroke={CHART_COLORS.primary} strokeWidth={2} dot={{ r: 3 }} name="Yorum" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel chart-panel">
            <h3 className="panel-title">Uyum Skorları Karşılaştırması</h3>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={fitData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: "var(--text-tertiary)" }} />
                  <YAxis tick={{ fontSize: 11, fill: "var(--text-tertiary)" }} />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Bar dataKey="odak" fill={CHART_COLORS.primary} name="Odak" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="ogrenme" fill={CHART_COLORS.purple} name="Öğrenme" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="eglence" fill={CHART_COLORS.pink} name="Eğlence" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

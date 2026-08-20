import { useCallback, useEffect, useState } from "react";
import {
  createComment,
  createPost,
  fetchComments,
  fetchCreators,
  fetchFeed,
  fetchWellbeing,
  previewAnalysis,
  toggleLike,
} from "./api";
import "./App.css";

const USERNAME = "meridyen_user";
const MODES = [
  {
    id: "odak",
    label: "Odak",
    hint: "Sakin, yapılandırılmış, düşük gürültü",
  },
  {
    id: "ogrenme",
    label: "Öğrenme",
    hint: "Açıklayıcı ve kavram yoğun içerik",
  },
  {
    id: "eglence",
    label: "Eğlence",
    hint: "Hafif, sosyal, toksik olmayan keyif",
  },
];

const PAGES = [
  { id: "akis", label: "Akış" },
  { id: "denge", label: "Denge raporu" },
  { id: "uretici", label: "Üretici alanı" },
];

function formatTime(value) {
  if (!value) return "Az önce";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Az önce";
  return date.toLocaleString("tr-TR", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function App() {
  const [mode, setMode] = useState("odak");
  const [page, setPage] = useState("akis");
  const [posts, setPosts] = useState([]);
  const [creators, setCreators] = useState([]);
  const [wellbeing, setWellbeing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [startedAt] = useState(() => Date.now());
  const [modeSwitches, setModeSwitches] = useState(0);
  const [sessionMinutes, setSessionMinutes] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [feed, economy, snapshot] = await Promise.all([
        fetchFeed(mode, USERNAME),
        fetchCreators(mode),
        fetchWellbeing(mode),
      ]);
      setPosts(feed);
      setCreators(economy.creators || []);
      setWellbeing(snapshot);
    } catch {
      setMessage("Sunucuya bağlanılamadı. Backend'in çalıştığından emin olun.");
    } finally {
      setLoading(false);
    }
  }, [mode]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setSessionMinutes(Math.max(1, Math.round((Date.now() - startedAt) / 60000)));
    }, 15000);
    return () => window.clearInterval(timer);
  }, [startedAt]);

  function changeMode(next) {
    if (next === mode) return;
    setMode(next);
    setModeSwitches((count) => count + 1);
    setMessage(`${MODES.find((item) => item.id === next)?.label} moduna geçildi.`);
  }

  const currentMode = MODES.find((item) => item.id === mode);

  return (
    <div className="shell" data-mode={mode}>
      <aside className="rail" aria-label="Ana menü">
        <div className="brand">
          <img className="brand-mark" src="/meridyen-logo.png" alt="Meridyen" />
          <div>
            <p className="brand-kicker">Dijital denge platformu</p>
            <h1>Meridyen</h1>
          </div>
        </div>

        <nav className="rail-nav">
          {PAGES.map((item) => (
            <button
              key={item.id}
              className={page === item.id ? "nav-btn active" : "nav-btn"}
              onClick={() => setPage(item.id)}
              aria-current={page === item.id ? "page" : undefined}
            >
              <span className="nav-orb" aria-hidden="true" />
              {item.label}
            </button>
          ))}
        </nav>

        <section className="rail-card" aria-live="polite">
          <p className="rail-card-label">Akış dengesi</p>
          <div className="rail-score">
            <span className="rail-score-value">{wellbeing?.score ?? "—"}</span>
            <span className="rail-score-unit">/ 100</span>
          </div>
          <div className="meter">
            <i style={{ width: `${wellbeing?.score || 0}%` }} />
          </div>
          <small>
            {wellbeing?.suppressed_count || 0} içerik filtrelendi
          </small>
        </section>

        <div className="rail-user">
          <div className="avatar">E</div>
          <div>
            <strong>Enes Yolcu</strong>
            <span>@{USERNAME}</span>
          </div>
        </div>
      </aside>

      <main className="stage">
        <div className="topbar">
          <div className="presence"><i /> Topluluğun için sakin bir alan</div>
          <div className="topbar-actions">
            <button type="button" className="icon-btn" aria-label="Bildirimler">⌁</button>
            <button type="button" className="profile-avatar" aria-label="Profil">E</button>
          </div>
        </div>
        <header className="stage-head">
          <div>
            <p className="eyebrow">Kişiselleştirilmiş deneyim</p>
            <h2>
              {page === "akis" && "Akış"}
              {page === "denge" && "Denge raporu"}
              {page === "uretici" && "Üretici alanı"}
            </h2>
            <p className="lede">
              Modunu seç; içeriğin güvenliği, faydası ve tonu göre sıralansın.
            </p>
          </div>

          <fieldset className="mode-switch" aria-label="Kullanım modu">
            <legend>Kullanım modu</legend>
            {MODES.map((item) => (
              <button
                key={item.id}
                type="button"
                aria-pressed={mode === item.id}
                className={mode === item.id ? "mode-chip on" : "mode-chip"}
                onClick={() => changeMode(item.id)}
              >
                {item.label}
              </button>
            ))}
          </fieldset>
        </header>

        <p className="mode-hint" role="status">
          {currentMode?.hint}
        </p>

        {message && (
          <div className="toast" role="status">
            <span>{message}</span>
            <button type="button" onClick={() => setMessage("")} aria-label="Kapat">
              ×
            </button>
          </div>
        )}

        {page === "akis" && (
          <FeedView
            posts={posts}
            loading={loading}
            mode={mode}
            onPosted={load}
            onMessage={setMessage}
          />
        )}

        {page === "denge" && (
          <BalanceView
            wellbeing={wellbeing}
            posts={posts}
            sessionMinutes={sessionMinutes}
            modeSwitches={modeSwitches}
            mode={mode}
          />
        )}

        {page === "uretici" && (
          <CreatorView creators={creators} mode={mode} />
        )}
      </main>
    </div>
  );
}

function FeedView({ posts, loading, mode, onPosted, onMessage }) {
  return (
    <div className="layout">
      <section>
        <Composer mode={mode} onPosted={onPosted} onMessage={onMessage} />
        <div className="feed-heading">
          <div>
            <span className="feed-label">Akış</span>
            <h3>Önerilen içerikler</h3>
          </div>
          <span className="live-dot"><i /> Güncelleme</span>
        </div>
        {loading ? (
          <div className="panel empty">İçerikler yükleniyor…</div>
        ) : (
          <ol className="feed">
            {posts.map((post, index) => (
              <PostCard
                key={`${post.id}-${mode}`}
                post={post}
                rank={index + 1}
                mode={mode}
                onMessage={onMessage}
              />
            ))}
          </ol>
        )}
      </section>

      <aside className="side">
        <article className="panel">
          <h3>Nasıl çalışır?</h3>
          <ul>
            <li>Seçtiğin mod, akışını biçimlendirir.</li>
            <li>Güvenlik ve fayda öncelikli sıralama.</li>
            <li>Her önerinin gerekçesi şeffaf.</li>
          </ul>
        </article>
        <article className="panel">
          <h3>Gizlilik ilkesi</h3>
          <ul>
            <li>Duygu tahmini yapılmaz; kontrol sende.</li>
            <li>Verilerin yalnızca senin deneyimini iyileştirir.</li>
            <li>İçerik tercihlerin üçüncü kişilerle paylaşılmaz.</li>
          </ul>
        </article>
      </aside>
    </div>
  );
}

function Composer({ mode, onPosted, onMessage }) {
  const [text, setText] = useState("");
  const [category, setCategory] = useState("Eğitim");
  const [preview, setPreview] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (text.trim().length < 8) {
      setPreview(null);
      return undefined;
    }

    const handle = window.setTimeout(async () => {
      try {
        const result = await previewAnalysis({
          title: text.slice(0, 80),
          description: text,
          category,
          mode,
        });
        setPreview(result);
      } catch {
        setPreview(null);
      }
    }, 350);

    return () => window.clearTimeout(handle);
  }, [text, category, mode]);

  async function publish() {
    if (!text.trim()) return;
    setBusy(true);
    try {
      const created = await createPost({
        author_username: USERNAME,
        display_name: "Enes Yolcu",
        content: text,
        category,
      });
      setText("");
      onPosted();
      if (!created.is_publishable) {
        onMessage("İçerik alındı; güvenlik filtresi nedeniyle görünürlüğü kısıtlandı.");
      } else {
        onMessage("İçerik yayınlandı.");
      }
    } catch (error) {
      onMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel composer">
      <label htmlFor="composer-input">Düşüncelerini paylaş</label>
      <textarea
        id="composer-input"
        value={text}
        maxLength={500}
        onChange={(event) => setText(event.target.value)}
        placeholder="Bir fikir, keşip ya da kısa bir not bırak…"
      />
      <div className="composer-bar">
        <select
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          aria-label="Kategori"
        >
          {["Eğitim", "Teknoloji", "Bilim", "Sanat", "Spor", "Genel"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <span>{text.length}/500</span>
        <button type="button" disabled={!text.trim() || busy} onClick={publish}>
          Paylaş
        </button>
      </div>
      {preview && (
        <div className="preview-bar" aria-live="polite">
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
  let tone = "badge-ok";
  if (v < 40) tone = "badge-warn";
  else if (v < 65) tone = "badge-mid";
  return (
    <span className={`preview-badge ${tone}`}>
      {label} <strong>{Math.round(v)}</strong>
    </span>
  );
}

function PostCard({ post, rank: _rank, mode, onMessage }) {
  const [open, setOpen] = useState(false);
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");
  const [liked, setLiked] = useState(post.liked_by_me);
  const [likeCount, setLikeCount] = useState(post.like_count);

  async function onLike() {
    try {
      const result = await toggleLike(post.id, USERNAME);
      setLiked(result.liked);
      setLikeCount(result.like_count);
    } catch (error) {
      onMessage(error.message);
    }
  }

  async function onToggleComments() {
    const next = !open;
    setOpen(next);
    if (next) {
      try {
        setComments(await fetchComments(post.id));
      } catch (error) {
        onMessage(error.message);
      }
    }
  }

  async function sendComment() {
    if (!commentText.trim()) return;
    try {
      const created = await createComment(post.id, USERNAME, commentText);
      setComments((current) => [...current, created]);
      setCommentText("");
    } catch (error) {
      onMessage(error.message);
    }
  }

  const modeFit = mode === "odak"
    ? post.focus_fit
    : mode === "ogrenme"
      ? post.learn_fit
      : post.fun_fit;

  return (
    <li className={post.is_publishable ? "card" : "card dimmed"}>
      <article>
        <header>
          <div className="avatar">{post.display_name[0]}</div>
          <div className="card-meta">
            <strong>{post.display_name}</strong>
            <span>
              @{post.author_username} · {formatTime(post.created_at)} · {post.category}
            </span>
          </div>
          <div className="card-fit-badge">
            <span className="fit-value">{Math.round(modeFit)}</span>
            <span className="fit-label">uyum</span>
          </div>
        </header>
        <p>{post.content}</p>
        {post.moderation_note && (
          <p className="warn">{post.moderation_note}</p>
        )}
        <dl className="score-chips">
          <div className="chip">
            <dt>Denge</dt>
            <dd>
              <span className="chip-bar">
                <i style={{ width: `${Math.min(post.wellbeing_score, 100)}%` }} />
              </span>
              <span className="chip-val">{Math.round(post.wellbeing_score)}</span>
            </dd>
          </div>
          <div className="chip">
            <dt>Güvenlik</dt>
            <dd>
              <span className="chip-bar">
                <i style={{ width: `${Math.min(post.safety_score, 100)}%` }} />
              </span>
              <span className="chip-val">{Math.round(post.safety_score)}</span>
            </dd>
          </div>
          <div className="chip">
            <dt>Erişim</dt>
            <dd>
              <span className="chip-val">×{post.visibility_multiplier.toFixed(2)}</span>
            </dd>
          </div>
        </dl>
        <details>
          <summary>Neden önerildi?</summary>
          <ul className="reason-list">
            {post.rank_reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </details>
        <footer>
          <button type="button" aria-pressed={liked} className={liked ? "liked" : ""} onClick={onLike}>
            {liked ? "Beğenildi" : "Beğen"} · {likeCount}
          </button>
          <button type="button" onClick={onToggleComments}>
            Yorum · {post.comment_count}
          </button>
        </footer>
        {open && (
          <div className="comments">
            {comments.map((comment) => (
              <p key={comment.id}>
                <strong>@{comment.username}</strong> {comment.content}
              </p>
            ))}
            <div className="comment-form">
              <input
                value={commentText}
                onChange={(event) => setCommentText(event.target.value)}
                placeholder="Yorum ekle"
                aria-label="Yorum"
              />
              <button type="button" onClick={sendComment}>
                Gönder
              </button>
            </div>
          </div>
        )}
      </article>
    </li>
  );
}

function BalanceView({ wellbeing, posts, sessionMinutes, modeSwitches, mode }) {
  const top = posts.slice(0, 3);
  const toxicShare = posts.length
    ? Math.round(
        (posts.filter((item) => item.safety_score < 70).length / posts.length) * 100
      )
    : 0;

  return (
    <div className="stat-grid">
      <article className="panel stat">
        <span className="stat-label">Ortalama denge</span>
        <strong className="stat-value">{wellbeing?.avg_wellbeing ?? 0}</strong>
      </article>
      <article className="panel stat">
        <span className="stat-label">Güvenli içerik</span>
        <strong className="stat-value">%{wellbeing?.safe_ratio ?? 0}</strong>
      </article>
      <article className="panel stat">
        <span className="stat-label">Oturum</span>
        <strong className="stat-value">{sessionMinutes || "<1"} dk</strong>
      </article>
      <article className="panel stat">
        <span className="stat-label">Mod değişimi</span>
        <strong className="stat-value">{modeSwitches}</strong>
      </article>
      <article className="panel span-2">
        <h3>Bu modda öne çıkanlar</h3>
        <p>
          Aktif mod: <strong>{mode}</strong> · Düşük güvenli içerik oranı %{toxicShare}.
        </p>
        <ol>
          {top.map((post) => (
            <li key={post.id}>
              {post.display_name} — {post.rank_score.toFixed(1)} · denge{" "}
              {Math.round(post.wellbeing_score)}
            </li>
          ))}
        </ol>
      </article>
    </div>
  );
}

function CreatorView({ creators }) {
  const mine = creators.find((item) => item.author_username === USERNAME);

  return (
    <div className="layout">
      <section className="panel">
        <h3>Haftalık gelir havuzu</h3>
        <p>
          Pay, görünürlük çarpanı ve refah skoruna göre dağıtılır.
        </p>
        {mine && (
          <p className="mine">
            Tahmini payınız: <strong>{mine.estimated_weekly_share} TL</strong>
          </p>
        )}
        <table className="board">
          <thead>
            <tr>
              <th>Üretici</th>
              <th>Refah</th>
              <th>Çarpan</th>
              <th>Pay</th>
            </tr>
          </thead>
          <tbody>
            {creators.map((creator) => (
              <tr
                key={creator.author_username}
                className={
                  creator.author_username === USERNAME ? "is-me" : undefined
                }
              >
                <td>{creator.display_name}</td>
                <td>{creator.avg_wellbeing}</td>
                <td>×{creator.avg_multiplier.toFixed(2)}</td>
                <td>{creator.estimated_weekly_share} TL</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <aside className="side">
        <article className="panel">
          <h3>Dağıtım mantığı</h3>
          <p>
            Kaliteli ve güvenli içerik daha fazla görünürlük kazanır.
            Tekil beğeni yerine bütüncül skorlama kullanılır.
          </p>
        </article>
      </aside>
    </div>
  );
}

export default App;

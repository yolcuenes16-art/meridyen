import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

const fallbackPosts = [
  {
    id: 2,
    author_username: "meridyen_user",
    content:
      "Yapay zeka ile öğrenme süreçlerimizi daha verimli ve bilinçli hale getirebiliriz.",
    category: "Eğitim",
    created_at: new Date().toISOString(),
    quality_score: 90,
    educational_score: 74,
    safety_score: 100,
    spam_score: 0,
    wellbeing_score: 90.5,
    overall_score: 88.62,
    is_publishable: true,
  },
];

function App() {
  const [posts, setPosts] = useState([]);
  const [activePage, setActivePage] = useState("Ana Sayfa");
  const [activeCategory, setActiveCategory] = useState("Tümü");
  const [newPost, setNewPost] = useState("");
  const [username] = useState("meridyen_user");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const categories = [
    { name: "Tümü", icon: "✨" },
    { name: "Eğitim", icon: "📚" },
    { name: "Teknoloji", icon: "💻" },
    { name: "Bilim", icon: "🔬" },
    { name: "Sanat", icon: "🎨" },
    { name: "Spor", icon: "⚽" },
  ];

  useEffect(() => {
    loadFeed();
  }, []);

  async function loadFeed() {
    setLoading(true);

    try {
      const response = await fetch(`${API}/api/v1/posts/feed`);

      if (!response.ok) {
        throw new Error("Feed alınamadı");
      }

      const data = await response.json();
      setPosts(Array.isArray(data) ? data : []);
    } catch {
      setPosts(fallbackPosts);
      setMessage("Demo içerik gösteriliyor.");
    } finally {
      setLoading(false);
    }
  }

  async function createPost() {
    if (!newPost.trim()) return;

    try {
      const response = await fetch(`${API}/api/v1/posts`, {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          author_username: username,
          content: newPost,
          category: activeCategory === "Tümü" ? "Genel" : activeCategory,
        }),
      });

      if (!response.ok) {
        throw new Error("Gönderi oluşturulamadı");
      }

      const created = await response.json();

      setPosts((current) => [created, ...current]);
      setNewPost("");
      setMessage("Gönderin başarıyla yayınlandı.");
    } catch {
      setMessage("Gönderi oluşturulurken bir hata oluştu.");
    }
  }

  async function likePost(postId) {
    try {
      await fetch(`${API}/api/v1/posts/${postId}/likes`, {
        method: "POST",
        headers: {
          accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
        }),
      });

      setMessage("Gönderi beğenildi.");
    } catch {
      setMessage("Beğeni işlemi gerçekleştirilemedi.");
    }
  }

  const filteredPosts = useMemo(() => {
    if (activeCategory === "Tümü") return posts;

    return posts.filter((post) => post.category === activeCategory);
  }, [posts, activeCategory]);

  function formatDate(date) {
    if (!date) return "Az önce";

    const value = new Date(date);

    if (Number.isNaN(value.getTime())) return "Az önce";

    return value.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "short",
    });
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">M</div>

          <div>
            <div className="brand-name">Meridyen</div>
            <div className="brand-subtitle">Smart Social</div>
          </div>
        </div>

        <nav className="main-nav">
          <button
            className={`nav-item ${activePage === "Ana Sayfa" ? "active" : ""}`}
            onClick={() => setActivePage("Ana Sayfa")}
          >
            <span>⌂</span>
            <span>Ana Sayfa</span>
          </button>

          <button
            className={`nav-item ${activePage === "Keşfet" ? "active" : ""}`}
            onClick={() => setActivePage("Keşfet")}
          >
            <span>◉</span>
            <span>Keşfet</span>
          </button>

          <button
            className={`nav-item ${activePage === "Topluluk" ? "active" : ""}`}
            onClick={() => setActivePage("Topluluk")}
          >
            <span>♧</span>
            <span>Topluluk</span>
          </button>

          <button
            className={`nav-item ${activePage === "Bildirimler" ? "active" : ""}`}
            onClick={() => setActivePage("Bildirimler")}
          >
            <span>♢</span>
            <span>Bildirimler</span>
            <span className="notification-dot">3</span>
          </button>

          <button
            className={`nav-item ${activePage === "Profil" ? "active" : ""}`}
            onClick={() => setActivePage("Profil")}
          >
            <span>○</span>
            <span>Profil</span>
          </button>
        </nav>

        <div className="sidebar-spacer" />

        <div className="wellbeing-card">
          <div className="wellbeing-top">
            <span className="wellbeing-icon">🧠</span>
            <span>Dijital Refah</span>
          </div>

          <div className="wellbeing-score">
            <strong>87</strong>
            <span>/ 100</span>
          </div>

          <div className="progress-track">
            <div className="progress-fill" style={{ width: "87%" }} />
          </div>

          <p>
            Bugünkü içerik tüketimin dengeli görünüyor.
          </p>

          <button
            onClick={() => setMessage("Dijital refah paneli yakında aktif olacak.")}
          >
            Refahımı Gör
          </button>
        </div>

        <div className="sidebar-user">
          <div className="avatar avatar-blue">M</div>

          <div className="user-info">
            <strong>{username}</strong>
            <span>Meridyen Kullanıcısı</span>
          </div>

          <button
            className="more-button"
            onClick={() => setMessage("Profil seçenekleri")}
          >
            ⋯
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="mobile-brand">Meridyen</div>
            <h1>{activePage}</h1>
            <p>
              Güvenli, kaliteli ve bilinçli sosyal deneyim.
            </p>
          </div>

          <div className="topbar-actions">
            <button
              className="icon-button"
              onClick={() => setMessage("Arama özelliği yakında aktif olacak.")}
            >
              ⌕
            </button>

            <button
              className="profile-button"
              onClick={() => setActivePage("Profil")}
            >
              <div className="avatar avatar-blue">M</div>
              <span>{username}</span>
              <span>⌄</span>
            </button>
          </div>
        </header>

        <section className="category-bar">
          {categories.map((category) => (
            <button
              key={category.name}
              className={
                activeCategory === category.name
                  ? "category-button selected"
                  : "category-button"
              }
              onClick={() => setActiveCategory(category.name)}
            >
              <span>{category.icon}</span>
              {category.name}
            </button>
          ))}
        </section>

        <div className="content-grid">
          <section className="feed-column">
            {activePage === "Ana Sayfa" || activePage === "Keşfet" ? (
              <>
                <section className="composer">
                  <div className="composer-header">
                    <div className="avatar avatar-blue">M</div>

                    <div>
                      <strong>Ne düşünüyorsun?</strong>
                      <span>Toplulukla paylaş.</span>
                    </div>
                  </div>

                  <textarea
                    value={newPost}
                    onChange={(event) => setNewPost(event.target.value)}
                    placeholder="Meridyen topluluğuyla faydalı bir şey paylaş..."
                    maxLength={500}
                  />

                  <div className="composer-footer">
                    <div className="composer-tools">
                      <button
                        onClick={() =>
                          setMessage("Görsel ekleme özelliği yakında geliyor.")
                        }
                      >
                        🖼️ Görsel
                      </button>

                      <button
                        onClick={() =>
                          setMessage("Kategori seçimi yukarıdaki menüden yapılabilir.")
                        }
                      >
                        # Kategori
                      </button>

                      <span>{newPost.length}/500</span>
                    </div>

                    <button
                      className="publish-button"
                      disabled={!newPost.trim()}
                      onClick={createPost}
                    >
                      Paylaş
                    </button>
                  </div>
                </section>

                {message && (
                  <div className="status-message">
                    <span>✓</span>
                    {message}
                    <button onClick={() => setMessage("")}>×</button>
                  </div>
                )}

                <div className="feed-heading">
                  <div>
                    <h2>
                      {activeCategory === "Tümü"
                        ? "Senin Akışın"
                        : `${activeCategory} Akışı`}
                    </h2>
                    <span>Senin için seçilen içerikler</span>
                  </div>

                  <button
                    className="sort-button"
                    onClick={loadFeed}
                  >
                    ↻ Yenile
                  </button>
                </div>

                {loading ? (
                  <div className="empty-state">
                    <div className="loading-circle" />
                    <h3>Akış hazırlanıyor...</h3>
                    <p>Meridyen içerikleri getiriliyor.</p>
                  </div>
                ) : filteredPosts.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">✦</div>
                    <h3>Henüz içerik yok</h3>
                    <p>İlk paylaşımı sen yapabilirsin.</p>
                  </div>
                ) : (
                  <div className="post-list">
                    {filteredPosts.map((post) => (
                      <article className="post-card" key={post.id}>
                        <div className="post-header">
                          <div className="avatar avatar-purple">
                            {(post.author_username || "M")[0].toUpperCase()}
                          </div>

                          <div className="post-author">
                            <div>
                              <strong>{post.author_username}</strong>

                              {post.is_publishable && (
                                <span className="verified">✓</span>
                              )}
                            </div>

                            <span>
                              {formatDate(post.created_at)} · {post.category}
                            </span>
                          </div>

                          <button
                            className="post-more"
                            onClick={() =>
                              setMessage("Gönderi seçenekleri yakında aktif.")
                            }
                          >
                            ⋯
                          </button>
                        </div>

                        <p className="post-content">{post.content}</p>

                        <div className="analysis-panel">
                          <div className="analysis-title">
                            <span>✦ Meridyen İçerik Analizi</span>
                            <strong>{post.overall_score ?? 0}/100</strong>
                          </div>

                          <div className="analysis-bars">
                            <ScoreBar
                              label="Kalite"
                              value={post.quality_score}
                            />
                            <ScoreBar
                              label="Eğiticilik"
                              value={post.educational_score}
                            />
                            <ScoreBar
                              label="Güvenlik"
                              value={post.safety_score}
                            />
                            <ScoreBar
                              label="Refah"
                              value={post.wellbeing_score}
                            />
                          </div>
                        </div>

                        <div className="post-actions">
                          <button onClick={() => likePost(post.id)}>
                            ♡ <span>Beğen</span>
                          </button>

                          <button
                            onClick={() =>
                              setMessage("Yorum alanı yakında aktif olacak.")
                            }
                          >
                            ◌ <span>Yorum</span>
                          </button>

                          <button
                            onClick={() =>
                              setMessage("Paylaşım özelliği yakında aktif olacak.")
                            }
                          >
                            ↗ <span>Paylaş</span>
                          </button>

                          <button
                            className="save-action"
                            onClick={() =>
                              setMessage("İçerik kaydedildi.")
                            }
                          >
                            ♧
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <PagePlaceholder
                page={activePage}
                onAction={() => setActivePage("Ana Sayfa")}
              />
            )}
          </section>

          <aside className="right-column">
            <section className="smart-card">
              <div className="smart-card-header">
                <div className="smart-icon">✦</div>

                <div>
                  <strong>Meridyen AI</strong>
                  <span>Akıllı içerik asistanı</span>
                </div>
              </div>

              <h3>Bugün senin için</h3>

              <p>
                İlgi alanlarına göre daha kaliteli ve dengeli içerikler
                keşfetmeye hazır mısın?
              </p>

              <button
                onClick={() => setActivePage("Keşfet")}
              >
                Keşfetmeye Başla <span>→</span>
              </button>
            </section>

            <section className="side-card">
              <div className="side-card-title">
                <h3>Trend Konular</h3>
                <button
                  onClick={() => setMessage("Tüm trendler yakında.")}
                >
                  Tümü
                </button>
              </div>

              <Trend
                number="01"
                title="Yapay Zeka"
                posts="1.284 gönderi"
              />

              <Trend
                number="02"
                title="Teknoloji"
                posts="932 gönderi"
              />

              <Trend
                number="03"
                title="Eğitim"
                posts="748 gönderi"
              />

              <Trend
                number="04"
                title="Dijital Refah"
                posts="421 gönderi"
              />
            </section>

            <section className="side-card people-card">
              <div className="side-card-title">
                <h3>Önerilenler</h3>
                <button
                  onClick={() => setMessage("Öneriler yenilendi.")}
                >
                  Yenile
                </button>
              </div>

              <Person
                letter="A"
                name="Ayşe Demir"
                username="@aysedemir"
              />

              <Person
                letter="K"
                name="Kerem Yılmaz"
                username="@keremy"
              />

              <Person
                letter="E"
                name="Elif Kaya"
                username="@elifkaya"
              />
            </section>

            <footer className="footer-links">
              <span>Meridyen</span>
              <span>Güvenlik</span>
              <span>Topluluk</span>
              <span>Hakkımızda</span>
              <small>© 2026 Meridyen</small>
            </footer>
          </aside>
        </div>
      </main>
    </div>
  );
}

function ScoreBar({ label, value = 0 }) {
  const safeValue = Math.max(0, Math.min(100, Number(value) || 0));

  return (
    <div className="score-item">
      <div>
        <span>{label}</span>
        <strong>{Math.round(safeValue)}</strong>
      </div>

      <div className="score-track">
        <div
          className="score-fill"
          style={{ width: `${safeValue}%` }}
        />
      </div>
    </div>
  );
}

function Trend({ number, title, posts }) {
  return (
    <div className="trend-item">
      <span className="trend-number">{number}</span>

      <div>
        <strong>#{title}</strong>
        <span>{posts}</span>
      </div>

      <span className="trend-arrow">↗</span>
    </div>
  );
}

function Person({ letter, name, username }) {
  return (
    <div className="person-item">
      <div className="avatar avatar-green">{letter}</div>

      <div className="person-info">
        <strong>{name}</strong>
        <span>{username}</span>
      </div>

      <button>Takip</button>
    </div>
  );
}

function PagePlaceholder({ page, onAction }) {
  const content = {
    Topluluk: {
      icon: "♧",
      title: "Topluluklar",
      text: "İlgi alanlarına göre topluluklar burada olacak.",
    },
    Bildirimler: {
      icon: "♢",
      title: "Bildirimler",
      text: "Etkileşimlerin ve önemli güncellemelerin burada görünecek.",
    },
    Profil: {
      icon: "○",
      title: "Profil",
      text: "Kişisel profil, gönderiler ve dijital refah istatistiklerin burada olacak.",
    },
  };

  const item = content[page] || {
    icon: "◉",
    title: page,
    text: "Bu bölüm hazırlanıyor.",
  };

  return (
    <div className="placeholder">
      <div className="placeholder-icon">{item.icon}</div>
      <h2>{item.title}</h2>
      <p>{item.text}</p>

      <button onClick={onAction}>Ana Sayfaya Dön</button>
    </div>
  );
}

export default App;
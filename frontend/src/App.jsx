import { useState } from "react";
import "./App.css";

const posts = [
  {
    id: 1,
    username: "meridyen_user",
    name: "Meridyen Kullanıcısı",
    category: "Eğitim",
    time: "12 dk",
    content:
      "Yapay zeka ile öğrenme süreçlerimizi daha verimli ve bilinçli hale getirebiliriz.",
    likes: 24,
    comments: 6,
    quality: 90,
    wellbeing: 91,
    safety: 100,
  },
  {
    id: 2,
    username: "gelecegininsani",
    name: "Geleceğin İnsanı",
    category: "Teknoloji",
    time: "28 dk",
    content:
      "Teknolojiyi daha fazla kullanmak değil, onu daha bilinçli kullanmak geleceğin en önemli becerilerinden biri olacak.",
    likes: 41,
    comments: 9,
    quality: 94,
    wellbeing: 88,
    safety: 100,
  },
  {
    id: 3,
    username: "yesilgelecek",
    name: "Yeşil Gelecek",
    category: "Çevre",
    time: "1 sa",
    content:
      "Küçük günlük alışkanlıklarımızı değiştirerek daha sürdürülebilir bir geleceğe katkı sağlayabiliriz.",
    likes: 67,
    comments: 13,
    quality: 96,
    wellbeing: 93,
    safety: 100,
  },
];

function App() {
  const [activePage, setActivePage] = useState("Ana Sayfa");
  const [likedPosts, setLikedPosts] = useState([]);
  const [showComposer, setShowComposer] = useState(false);
  const [newPost, setNewPost] = useState("");

  const toggleLike = (id) => {
    setLikedPosts((current) =>
      current.includes(id)
        ? current.filter((postId) => postId !== id)
        : [...current, id]
    );
  };

  const menu = [
    { icon: "⌂", label: "Ana Sayfa" },
    { icon: "⌕", label: "Keşfet" },
    { icon: "✦", label: "Meridyen Analiz" },
    { icon: "♡", label: "Etkileşimler" },
    { icon: "◷", label: "Dijital Refah" },
  ];

  return (
    <div className="app">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">M</div>
          <div>
            <div className="brand-name">meridyen</div>
            <div className="brand-subtitle">dijital sosyal platform</div>
          </div>
        </div>

        <nav className="navigation">
          {menu.map((item) => (
            <button
              key={item.label}
              className={`nav-item ${
                activePage === item.label ? "active" : ""
              }`}
              onClick={() => setActivePage(item.label)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <button
          className="create-button"
          onClick={() => setShowComposer(true)}
        >
          <span>＋</span>
          Gönderi Oluştur
        </button>

        <div className="sidebar-bottom">
          <div className="wellbeing-mini">
            <div className="mini-title">
              <span>✦</span> Dijital Refah
            </div>

            <div className="mini-score">
              <strong>87</strong>
              <span>/100</span>
            </div>

            <div className="progress">
              <div className="progress-fill" style={{ width: "87%" }} />
            </div>

            <p>Bugün dengeli bir kullanım sergiliyorsun.</p>
          </div>

          <div className="profile-mini">
            <div className="avatar">M</div>
            <div>
              <strong>meridyen_user</strong>
              <span>Profilim</span>
            </div>
            <span className="more">•••</span>
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="main">
        <header className="topbar">
          <div>
            <div className="page-label">SOSYAL ALAN</div>
            <h1>{activePage}</h1>
          </div>

          <div className="top-actions">
            <div className="search">
              <span>⌕</span>
              <input placeholder="Meridyen'de ara..." />
            </div>

            <button className="notification">♧</button>

            <div className="top-avatar">M</div>
          </div>
        </header>

        {activePage === "Ana Sayfa" && (
          <div className="content-layout">
            <section className="feed">
              <div className="welcome">
                <div>
                  <span className="eyebrow">MERİDYEN AKIŞI</span>
                  <h2>Bugün ne keşfetmek istersin?</h2>
                  <p>
                    Sana uygun, kaliteli ve dijital refahını gözeten içerikler.
                  </p>
                </div>

                <div className="welcome-symbol">✦</div>
              </div>

              <div className="composer-short" onClick={() => setShowComposer(true)}>
                <div className="avatar">M</div>
                <span>Aklından neler geçiyor?</span>
                <button>Gönderi oluştur</button>
              </div>

              {posts.map((post) => (
                <article className="post-card" key={post.id}>
                  <div className="post-header">
                    <div className="avatar">{post.name.charAt(0)}</div>

                    <div className="author">
                      <strong>{post.name}</strong>
                      <span>
                        @{post.username} · {post.time}
                      </span>
                    </div>

                    <span className="category">{post.category}</span>

                    <button className="post-more">•••</button>
                  </div>

                  <div className="post-content">{post.content}</div>

                  <div className="analysis-strip">
                    <div className="analysis-title">
                      <span>✦</span>
                      Meridyen İçerik Analizi
                    </div>

                    <div className="scores">
                      <span>
                        Kalite <b>{post.quality}</b>
                      </span>
                      <span>
                        Refah <b>{post.wellbeing}</b>
                      </span>
                      <span>
                        Güvenlik <b>{post.safety}</b>
                      </span>
                    </div>

                    <span className="safe">✓ Güvenli içerik</span>
                  </div>

                  <div className="post-footer">
                    <button
                      className={likedPosts.includes(post.id) ? "liked" : ""}
                      onClick={() => toggleLike(post.id)}
                    >
                      {likedPosts.includes(post.id) ? "♥" : "♡"}{" "}
                      {post.likes + (likedPosts.includes(post.id) ? 1 : 0)}
                    </button>

                    <button>◯ {post.comments}</button>
                    <button>↗ Paylaş</button>

                    <button className="save">◇</button>
                  </div>
                </article>
              ))}
            </section>

            {/* RIGHT PANEL */}
            <aside className="right-panel">
              <div className="panel">
                <div className="panel-heading">
                  <div>
                    <span className="eyebrow">SANA ÖZEL</span>
                    <h3>Meridyen Skoru</h3>
                  </div>

                  <span className="sparkle">✦</span>
                </div>

                <div className="big-score">
                  <div className="score-circle">
                    <strong>87</strong>
                    <span>/100</span>
                  </div>

                  <div>
                    <strong>Çok iyi gidiyorsun.</strong>
                    <p>
                      İçerik tüketim alışkanlıkların dengeli.
                    </p>
                  </div>
                </div>

                <div className="score-row">
                  <span>İçerik kalitesi</span>
                  <strong>92</strong>
                </div>

                <div className="score-row">
                  <span>Dijital denge</span>
                  <strong>87</strong>
                </div>

                <div className="score-row">
                  <span>Güvenli etkileşim</span>
                  <strong>96</strong>
                </div>
              </div>

              <div className="panel explore">
                <span className="eyebrow">KEŞFET</span>
                <h3>İlgi alanların</h3>

                <div className="tags">
                  <span>Yapay Zeka</span>
                  <span>Eğitim</span>
                  <span>Teknoloji</span>
                  <span>Çevre</span>
                  <span>Bilim</span>
                </div>
              </div>

              <div className="panel principle">
                <div className="principle-icon">✦</div>
                <div>
                  <span className="eyebrow">MERİDYEN İLKESİ</span>
                  <p>
                    Daha fazla içerik değil, <strong>daha iyi içerik.</strong>
                  </p>
                </div>
              </div>
            </aside>
          </div>
        )}

        {activePage !== "Ana Sayfa" && (
          <section className="placeholder">
            <div className="placeholder-icon">✦</div>
            <span className="eyebrow">MERİDYEN</span>
            <h2>{activePage}</h2>
            <p>
              Bu bölümün arayüzünü ve gerçek API bağlantılarını bir sonraki
              aşamada oluşturacağız.
            </p>
          </section>
        )}
      </main>

      {/* CREATE POST MODAL */}
      {showComposer && (
        <div
          className="modal-backdrop"
          onClick={() => setShowComposer(false)}
        >
          <div
            className="modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <span className="eyebrow">MERİDYEN</span>
                <h2>Yeni gönderi</h2>
              </div>

              <button onClick={() => setShowComposer(false)}>×</button>
            </div>

            <div className="modal-user">
              <div className="avatar">M</div>
              <strong>meridyen_user</strong>
            </div>

            <textarea
              value={newPost}
              onChange={(event) => setNewPost(event.target.value)}
              placeholder="Düşüncelerini toplulukla paylaş..."
              autoFocus
            />

            <div className="modal-info">
              <span>✦</span>
              Gönderin paylaşılmadan önce Meridyen tarafından analiz edilir.
            </div>

            <div className="modal-footer">
              <button
                className="cancel"
                onClick={() => setShowComposer(false)}
              >
                Vazgeç
              </button>

              <button
                className="publish"
                disabled={!newPost.trim()}
                onClick={() => {
                  setShowComposer(false);
                  setNewPost("");
                }}
              >
                Paylaş
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
const API = "/api/v1";

export async function registerUser({ username, password, display_name, bio, category }) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password, display_name, bio, category }),
  });
}

export async function loginUser({ username, password }) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function fetchMe() {
  return request("/auth/me");
}

export async function refreshToken(token) {
  return request("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

async function request(path, options = {}) {
  const token = localStorage.getItem("meridyen-token");
  const response = await fetch(`${API}${path}`, {
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    const msg = Array.isArray(detail.detail)
      ? detail.detail.map((e) => e.msg || String(e)).join(", ")
      : (detail.detail || "İstek başarısız oldu.");
    throw new Error(msg);
  }

  return response.json();
}

export function fetchFeed(mode, viewer, { page = 1, limit = 10 } = {}) {
  const params = new URLSearchParams({
    mode,
    viewer,
    page: String(page),
    limit: String(limit),
  });
  return request(`/posts/feed?${params.toString()}`);
}

export function createPost(payload) {
  return request("/posts", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function toggleLike(postId, username) {
  return request(`/posts/${postId}/likes`, {
    method: "POST",
    body: JSON.stringify({ username }),
  });
}

export function fetchComments(postId) {
  return request(`/posts/${postId}/comments`);
}

export function createComment(postId, username, content) {
  return request(`/posts/${postId}/comments`, {
    method: "POST",
    body: JSON.stringify({ username, content }),
  });
}

export function fetchCreators(mode) {
  return request(`/economy/creators?mode=${encodeURIComponent(mode)}`);
}

export function fetchWellbeing(mode) {
  return request(`/economy/wellbeing?mode=${encodeURIComponent(mode)}`);
}

export function previewAnalysis({ title, description, category, mode }) {
  return request("/analysis/preview", {
    method: "POST",
    body: JSON.stringify({ title, description, category, mode }),
  });
}

export function fetchGamification(username) {
  return request(`/gamification/${username}`);
}

export function toggleBookmark(postId, username) {
  return request(`/posts/${postId}/bookmarks`, {
    method: "POST",
    body: JSON.stringify({ username }),
  });
}

export function fetchUserBookmarks(username) {
  return request(`/users/${username}/bookmarks`);
}

export function reportPost(postId, username, reason) {
  return request(`/posts/${postId}/reports`, {
    method: "POST",
    body: JSON.stringify({ username, reason }),
  });
}

export function fetchTrending(mode) {
  return request(`/posts/trending?mode=${encodeURIComponent(mode)}`);
}

export function summarizeContent(content) {
  return request("/analysis/summarize", {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export async function aiAssistant(prompt, mode = "odak") {
  const result = await previewAnalysis({
    title: prompt.slice(0, 80),
    description: prompt,
    category: "Genel",
    mode,
  });

  const a = result.analysis || {};
  const lines = [];

  lines.push("Meridyen Yapay Zekâ Asistanı girdinizi analiz ediyor:");
  lines.push("");

  if (a.safety_score !== undefined) {
    const safe = Math.round(a.safety_score);
    if (safe >= 80) lines.push("Güvenlik: İçeriğiniz yüksek güvenlik skoruna sahip (" + safe + "/100). Topluluk standartlarına tam uyumlu.");
    else if (safe >= 50) lines.push("Güvenlik: İçeriğiniz orta seviyede (" + safe + "/100). Bazı ifadeler incelenebilir.");
    else lines.push("Güvenlik: İçeriğiniz düşük güvenlik skoruna sahip (" + safe + "/100). Lütfen içeriğinizi gözden geçirin.");
  }

  if (a.wellbeing_score !== undefined) {
    const wb = Math.round(a.wellbeing_score);
    if (wb >= 70) lines.push("Fayda: İçeriğiniz topluluk için faydalı ve pozitif bir etki yaratıyor (" + wb + "/100).");
    else if (wb >= 40) lines.push("Fayda: İçeriğiniz orta düzeyde fayda sağlıyor (" + wb + "/100).");
    else lines.push("Fayda: İçeriğinizin topluluk katkısı düşük (" + wb + "/100). Daha faydalı bir içerik oluşturmayı deneyin.");
  }

  if (a.sentiment !== undefined) {
    const sent = a.sentiment;
    if (sent > 0.3) lines.push("Duygu: İçerik olumlu ve yapıcı bir tona sahip.");
    else if (sent < -0.3) lines.push("Duygu: İçerik olumsuz bir ton taşıyor. Daha yapıcı bir dil kullanmayı deneyin.");
    else lines.push("Duygu: İçerik nötr bir tonda.");
  }

  if (result.ranking) {
    const vis = result.ranking.visibility_multiplier;
    if (vis) lines.push("Görünürlük Çarpanı: ×" + Number(vis).toFixed(2) + " — İçeriğinizin erişim potansiyeli hesaplandı.");
  }

  if (a.flags && a.flags.length > 0) {
    lines.push("");
    lines.push("Dikkat Edilmesi Gerekenler:");
    a.flags.forEach(function(f) { lines.push("  • " + f); });
  }

  if (result.ranking && result.ranking.reasons && result.ranking.reasons.length > 0) {
    lines.push("");
    lines.push("Sıralama Gerekçeleri:");
    result.ranking.reasons.forEach(function(r) { lines.push("  • " + r); });
  }

  return lines.join("\n");
}

export async function editPost(postId, data) {
  return request(`/posts/${postId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deletePost(postId, username) {
  return request(`/posts/${postId}`, {
    method: "DELETE",
    body: JSON.stringify({ username }),
  });
}

export async function searchContent(params) {
  return request(`/search?${new URLSearchParams(params)}`);
}

export async function fetchTrendingHashtags() {
  return request("/hashtags/trending");
}

export async function fetchHashtagPosts(tag, params) {
  return request(`/hashtags/${tag}/posts?${new URLSearchParams(params)}`);
}

export async function followUser(targetUsername, followerUsername) {
  return request(`/users/${targetUsername}/follow`, {
    method: "POST",
    body: JSON.stringify({ follower_username: followerUsername }),
  });
}

export async function unfollowUser(targetUsername, followerUsername) {
  return request(`/users/${targetUsername}/unfollow`, {
    method: "DELETE",
    body: JSON.stringify({ follower_username: followerUsername }),
  });
}

export async function fetchFollowers(username) {
  return request(`/users/${username}/followers`);
}

export async function fetchFollowing(username) {
  return request(`/users/${username}/following`);
}

export async function updateProfile(data) {
  return request("/users/me", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

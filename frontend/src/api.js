const API = "/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || "İstek başarısız oldu.");
  }

  return response.json();
}

export function fetchFeed(mode, viewer) {
  const params = new URLSearchParams({
    mode,
    viewer,
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

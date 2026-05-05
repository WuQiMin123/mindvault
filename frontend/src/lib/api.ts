const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface TagResponse {
  id: number;
  name: string;
  color: string | null;
  link_count: number;
}

export interface LinkResponse {
  id: number;
  url: string | null;
  title: string;
  content: string | null;
  raw_content: string | null;
  source: string;
  summary: string | null;
  tags: TagResponse[];
  status: string;
  error: string | null;
  is_read: number;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface TagSummaryResponse {
  tag: TagResponse;
  links: LinkResponse[];
  aggregate_summary: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  // Links
  listLinks(params?: {
    page?: number;
    page_size?: number;
    tag?: string;
    source?: string;
    status?: string;
    search?: string;
  }): Promise<PaginatedResponse<LinkResponse>> {
    const q = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => { if (v) q.set(k, String(v)); });
    }
    return request(`/links?${q}`);
  },

  getLink(id: number): Promise<LinkResponse> {
    return request(`/links/${id}`);
  },

  deleteLink(id: number): Promise<void> {
    return request(`/links/${id}`, { method: "DELETE" });
  },

  updateReadStatus(id: number, is_read: boolean): Promise<void> {
    return request(`/links/${id}/read-status`, {
      method: "PATCH",
      body: JSON.stringify({ is_read }),
    });
  },

  analyzeLink(id: number): Promise<void> {
    return request(`/links/${id}/analyze`, { method: "POST" });
  },

  updateLinkContent(id: number, content: string, title?: string): Promise<LinkResponse> {
    return request(`/links/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ content, title }),
    });
  },

  // Ingest
  ingestLink(url: string, tags?: string[]): Promise<{ id: number }> {
    return request("/ingest/link", {
      method: "POST",
      body: JSON.stringify({ url, tags: tags || [] }),
    });
  },

  bookmarkLink(url: string): Promise<{ id: number }> {
    return request("/ingest/bookmark", {
      method: "POST",
      body: JSON.stringify({ url }),
    });
  },

  ingestText(title: string, content: string, tags?: string[]): Promise<{ id: number }> {
    return request("/ingest/text", {
      method: "POST",
      body: JSON.stringify({ title, content, tags: tags || [] }),
    });
  },

  checkLink(url: string): Promise<{ exists: boolean; link_id?: number }> {
    return request(`/ingest/check?url=${encodeURIComponent(url)}`);
  },

  // Tags
  listTags(): Promise<TagResponse[]> {
    return request("/tags");
  },

  createTag(name: string, color?: string): Promise<TagResponse> {
    return request("/tags", {
      method: "POST",
      body: JSON.stringify({ name, color }),
    });
  },

  deleteTag(id: number): Promise<void> {
    return request(`/tags/${id}`, { method: "DELETE" });
  },

  getTagSummary(id: number): Promise<TagSummaryResponse> {
    return request(`/tags/${id}/summary`);
  },

  updateLinkTags(linkId: number, tagIds: number[]): Promise<void> {
    return request(`/tags/links/${linkId}/tags`, {
      method: "PUT",
      body: JSON.stringify({ tag_ids: tagIds }),
    });
  },

  // Search
  search(params: { q: string; tag_ids?: string; page?: number }): Promise<PaginatedResponse<LinkResponse>> {
    const q = new URLSearchParams();
    q.set("q", params.q);
    if (params.tag_ids) q.set("tag_ids", params.tag_ids);
    if (params.page) q.set("page", String(params.page));
    return request(`/search?${q}`);
  },
};

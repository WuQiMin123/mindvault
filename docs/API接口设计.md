# API 接口设计

基础路径: `/api/v1`

## 健康检查

### GET /health
```
Response: { "status": "ok" }
```

## 内容摄入 (Ingest)

### POST /api/v1/ingest/text
手动添加内容。

```
Request:
{
  "title": "我的笔记",
  "content": "纯文本内容...",
  "url": "",
  "tags": ["笔记", "技术"]
}

Response 201:
{
  "id": 2,
  "title": "我的笔记",
  "status": "completed"
}
```

## 链接管理 (Links)

### GET /api/v1/links
获取内容列表。

```
Query:
  page: int = 1
  page_size: int = 20
  tag: str = ""
  source: str = ""
  search: str = ""
  status: str = ""

Response:
{
  "items": [
    {
      "id": 1,
      "url": "...",
      "title": "...",
      "source": "manual",
      "content": "...",
      "summary": "...",
      "tags": [{"id": 1, "name": "AI", "color": "#3b82f6"}],
      "status": "completed",
      "error": null,
      "is_read": 0,
      "created_at": "2026-05-04 10:00:00",
      "updated_at": "2026-05-04 10:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### GET /api/v1/links/{id}
获取单条内容详情。

```
Response:
{
  "id": 1,
  "url": "...",
  "title": "...",
  "content": "...",
  "raw_content": "...",
  "source": "manual",
  "summary": "...",
  "tags": [...],
  "status": "completed",
  "error": null,
  "is_read": 0,
  "created_at": "...",
  "updated_at": "..."
}
```

### DELETE /api/v1/links/{id}
删除内容。

```
Response 204: No Content
```

### PATCH /api/v1/links/{id}
修改内容。

```
Request:
{
  "content": "手动更新的正文内容...",
  "title": "可选的新标题"
}

Response 200:
{
  "id": 1,
  "content": "...",
  "title": "...",
  "tags": [...],
  "status": "completed"
}
```

### PATCH /api/v1/links/{id}/read-status
更新阅读状态。

```
Request:  { "is_read": true }
Response: { "id": 1, "is_read": true }
```

## 标签管理 (Tags)

### GET /api/v1/tags
获取所有标签。

```
Response:
[
  {
    "id": 1,
    "name": "AI",
    "color": "#3b82f6",
    "link_count": 15
  }
]
```

### POST /api/v1/tags
创建标签。

```
Request:  { "name": "AI", "color": "#3b82f6" }
Response: { "id": 1, "name": "AI", "color": "#3b82f6" }
```

### PUT /api/v1/tags/{id}
更新标签。

```
Request:  { "name": "人工智能", "color": "#ef4444" }
Response: { "id": 1, "name": "人工智能", "color": "#ef4444" }
```

### DELETE /api/v1/tags/{id}
删除标签。

```
Response 204: No Content
```

### PUT /api/v1/links/{link_id}/tags
更新某条内容的标签。

```
Request:  { "tag_ids": [1, 2, 3] }
Response: { "tag_ids": [1, 2, 3] }
```

## 标签聚合 (Tag Summary)

### GET /api/v1/tags/{id}/summary

```
Response:
{
  "tag": { "id": 1, "name": "AI", "color": "#3b82f6" },
  "links": [
    {"id": 1, "title": "...", "summary": "..."}
  ],
  "aggregate_summary": "该标签下的内容主要涉及..."
}
```

## 搜索 (Search)

### GET /api/v1/search
全文搜索。

```
Query:
  q: string
  tag_ids: string = ""
  page: int = 1
  page_size: int = 20

Response:
{
  "items": [...],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

## 数据导出 (Export)

### GET /api/v1/export/json
导出全部数据为 JSON 格式。

### GET /api/v1/export/markdown
导出全部数据为 Markdown ZIP 包。

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功 |
| 400 | 参数错误 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如标签重名） |
| 422 | 参数校验失败 |

## 错误响应格式

```json
{
  "detail": "链接不存在"
}
```
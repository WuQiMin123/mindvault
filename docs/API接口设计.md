# API 接口设计

基础路径: `/api/v1`

## 健康检查

### GET /health
```
Response: { "status": "ok" }
```

## 内容摄入 (Ingest) (v1)

### POST /api/v1/ingest/link
提交链接进行抓取和处理。

```
Request:
{
  "url": "https://www.bilibili.com/video/BV1xx411c7mD",
  "tags": []
}

Response 202:
{
  "id": 1,
  "status": "pending",
  "message": "内容正在抓取处理"
}
```

### POST /api/v1/ingest/bookmark
快速暂存链接（不分析，仅保存链接，后续手动触发分析）。

```
Request:
{
  "url": "https://www.bilibili.com/video/BV1xx411c7mD"
}

Response 201:
{
  "id": 1,
  "status": "completed",
  "message": "链接已暂存"
}
```

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

### POST /api/v1/ingest/check
提交前检查链接是否已存在。

```
Request:
{
  "url": "https://www.bilibili.com/video/BV1xx411c7mD"
}

Response:
{
  "exists": true,
  "link_id": 1,
  "title": "已有的标题"
}
```

## 链接管理 (Links) (v1)

### GET /api/v1/links
获取链接列表。

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
      "source": "bilibili",
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
获取单条链接详情。

```
Response:
{
  "id": 1,
  "url": "...",
  "title": "...",
  "content": "...",
  "raw_content": "...",
  "source": "bilibili",
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
删除链接。

```
Response 204: No Content
```

### PATCH /api/v1/links/{id}
手动补充内容并触发重新分析。

```
Request:
{
  "content": "手动粘贴的正文内容...",
  "title": "可选的新标题"
}

Response 200:
{
  "id": 1,
  "content": "...",
  "status": "pending",
  "tags": [...],
  "error": null
}
```

> 用于 status = no_content 的链接：粘贴内容后保存，后台 AI 管线重新生成摘要和标签，同时移除"未成功"标签。

### PATCH /api/v1/links/{id}/read-status
更新阅读状态。

```
Request:  { "is_read": true }
Response: { "id": 1, "is_read": true }
```

### POST /api/v1/links/{id}/analyze
触发分析管线。

```
Response 202:
{
  "id": 1,
  "status": "pending",
  "message": "开始分析该链接"
}
```

## 标签管理 (Tags) (v1)

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
更新某个链接的标签。

```
Request:  { "tag_ids": [1, 2, 3] }
Response: { "tag_ids": [1, 2, 3] }
```

## 标签聚合 (Tag Summary) (v1)

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

## 搜索 (Search) (v1)

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
  "items": [
    {
      "id": 1,
      "title": "...",
      "content": "...",
      "source": "bilibili",
      "summary": "...",
      "tags": [...],
      "created_at": "..."
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 202 | 异步任务已接受 |
| 204 | 删除成功 |
| 400 | 参数错误 |
| 404 | 资源不存在 |
| 422 | 参数校验失败 |

## 错误响应格式

```json
{
  "detail": "链接不存在"
}
```

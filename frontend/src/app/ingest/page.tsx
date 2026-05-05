"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type Mode = "link" | "text" | "bookmark";

export default function IngestPage() {
  const [mode, setMode] = useState<Mode>("link");
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");
    setError("");
    const tagList = tags
      .split(/[,，]/)
      .map((t) => t.trim())
      .filter(Boolean);

    try {
      if (mode === "bookmark") {
        const r = await api.bookmarkLink(url);
        setMessage(`已暂存 (ID: ${r.id})`);
        setUrl("");
      } else if (mode === "link") {
        const r = await api.ingestLink(url, tagList);
        setMessage(`提交成功，正在分析 (ID: ${r.id})`);
        setUrl("");
        setTags("");
      } else {
        const r = await api.ingestText(title, content, tagList);
        setMessage(`已保存 (ID: ${r.id})`);
        setTitle("");
        setContent("");
        setTags("");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "提交失败");
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">提交内容</h1>

      <Card>
        <CardHeader>
          <CardTitle>选择提交方式</CardTitle>
        </CardHeader>
        <CardContent>
          <Select
            value={mode}
            onValueChange={(v) => {
              if (v) {
                setMode(v as Mode);
                setMessage("");
                setError("");
              }
            }}
          >
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="link">链接 (自动分析)</SelectItem>
              <SelectItem value="bookmark">链接 (仅暂存)</SelectItem>
              <SelectItem value="text">纯文本/笔记</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <form onSubmit={handleSubmit} className="space-y-4">
        {mode !== "text" ? (
          <div className="space-y-2">
            <label className="text-sm font-medium">URL</label>
            <Input
              placeholder="https://..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
          </div>
        ) : (
          <>
            <div className="space-y-2">
              <label className="text-sm font-medium">标题</label>
              <Input
                placeholder="笔记标题"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">内容</label>
              <Textarea
                placeholder="粘贴或输入内容..."
                rows={8}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                required
              />
            </div>
          </>
        )}

        {mode !== "bookmark" && (
          <div className="space-y-2">
            <label className="text-sm font-medium">标签 (逗号分隔)</label>
            <Input
              placeholder="AI, 技术, 笔记"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
            />
          </div>
        )}

        <Button type="submit">提交</Button>

        {message && <p className="text-sm text-green-600">{message}</p>}
        {error && <p className="text-sm text-destructive">{error}</p>}
      </form>
    </div>
  );
}

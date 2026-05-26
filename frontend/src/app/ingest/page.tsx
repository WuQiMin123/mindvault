"use client";

import { useEffect, useState } from "react";
import { api, type TagResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export default function IngestPage() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tagInput, setTagInput] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [allTags, setAllTags] = useState<TagResponse[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.listTags().then(setAllTags).catch(() => {});
  }, []);

  const availableTags = allTags.filter((t) => !selectedTags.includes(t.name));

  function addTag(name: string) {
    if (name && !selectedTags.includes(name)) {
      setSelectedTags((prev) => [...prev, name]);
    }
  }

  function removeTag(name: string) {
    setSelectedTags((prev) => prev.filter((t) => t !== name));
  }

  function handleAddTag() {
    const t = tagInput.trim();
    if (t) {
      addTag(t);
      setTagInput("");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");
    setError("");
    setSubmitting(true);

    try {
      const r = await api.ingestText(title, content, selectedTags);
      setMessage(`已保存 (ID: ${r.id})`);
      setTitle("");
      setContent("");
      setSelectedTags([]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "提交失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">提交内容</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
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

        <div className="space-y-2">
          <label className="text-sm font-medium">已有标签</label>
          {availableTags.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {availableTags.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  className="inline-flex items-center rounded-full border border-dashed border-border px-2.5 py-0.5 text-xs text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors cursor-pointer"
                  onClick={() => addTag(t.name)}
                >
                  {t.name}
                </button>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">暂无标签，请在下方创建</p>
          )}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">新建 / 搜索标签</label>
          <div className="flex gap-2">
            <Input
              placeholder="输入标签名"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddTag())}
            />
            <Button type="button" variant="outline" onClick={handleAddTag}>
              添加
            </Button>
          </div>
        </div>

        {selectedTags.length > 0 && (
          <div className="space-y-2">
            <label className="text-sm font-medium">已选标签</label>
            <div className="flex flex-wrap gap-1.5">
              {selectedTags.map((name) => (
                <span
                  key={name}
                  className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs text-primary"
                >
                  {name}
                  <button
                    type="button"
                    className="text-primary/50 hover:text-primary cursor-pointer"
                    onClick={() => removeTag(name)}
                  >
                    &times;
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        <Button type="submit" disabled={submitting}>
          {submitting ? "提交中..." : "提交"}
        </Button>

        {message && <p className="text-sm text-green-600">{message}</p>}
        {error && <p className="text-sm text-destructive">{error}</p>}
      </form>
    </div>
  );
}
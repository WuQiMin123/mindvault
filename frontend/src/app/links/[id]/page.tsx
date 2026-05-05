"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, type LinkResponse, type TagResponse } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TagBadge } from "@/components/tag-badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function LinkDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [link, setLink] = useState<LinkResponse | null>(null);
  const [allTags, setAllTags] = useState<TagResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [selectedTagId, setSelectedTagId] = useState("");
  const [manualContent, setManualContent] = useState("");
  const [saving, setSaving] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const linkId = Number(params.id);

  const load = useCallback(async () => {
    const [l, tags] = await Promise.all([
      api.getLink(linkId),
      api.listTags(),
    ]);
    setLink(l);
    setAllTags(tags);
    setLoading(false);
    return l;
  }, [linkId]);

  // 轮询：当状态为 pending 时，每隔 2s 刷新直到完成
  const startPolling = useCallback(() => {
    if (pollRef.current) return;
    pollRef.current = setInterval(async () => {
      const l = await api.getLink(linkId);
      setLink(l);
      if (l.status !== "pending") {
        if (pollRef.current) {
          clearInterval(pollRef.current);
          pollRef.current = null;
        }
        setAnalyzing(false);
      }
    }, 2000);
  }, [linkId]);

  useEffect(() => {
    load().then((l) => {
      if (l && l.status === "pending") {
        setAnalyzing(true);
        startPolling();
      }
    });
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [load, startPolling]);

  async function handleAddTag() {
    if (!selectedTagId || !link) return;
    const currentIds = link.tags.map((t) => t.id);
    await api.updateLinkTags(link.id, [...currentIds, Number(selectedTagId)]);
    setSelectedTagId("");
    load();
  }

  async function handleRemoveTag(tagId: number) {
    if (!link) return;
    const newIds = link.tags.filter((t) => t.id !== tagId).map((t) => t.id);
    await api.updateLinkTags(link.id, newIds);
    load();
  }

  async function handleDelete() {
    if (!confirm("确定删除？")) return;
    setDeleting(true);
    await api.deleteLink(linkId);
    router.push("/");
  }

  async function handleAnalyze() {
    if (!link) return;
    setAnalyzing(true);
    await api.analyzeLink(link.id);
    startPolling();
  }

  async function handleSaveManualContent() {
    if (!link || !manualContent.trim()) return;
    setSaving(true);
    await api.updateLinkContent(link.id, manualContent);
    setManualContent("");
    setAnalyzing(true);
    startPolling();
  }

  if (loading) return <div className="text-center text-muted-foreground py-12">加载中...</div>;
  if (!link) return <div className="text-center text-muted-foreground py-12">链接不存在</div>;

  const availableTags = allTags.filter((t) => !link.tags.some((lt) => lt.id === t.id));

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <button
        className="text-sm text-muted-foreground hover:underline cursor-pointer"
        onClick={() => router.back()}
      >
        &larr; 返回
      </button>

      <h1 className="text-2xl font-bold">{link.title}</h1>

      {/* 标签编辑 */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">标签</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-2">
            {link.tags.map((t) => (
              <span key={t.id} className="group relative">
                <TagBadge name={t.name} color={t.color} />
                <button
                  className="absolute -top-1.5 -right-1.5 hidden size-3.5 cursor-pointer items-center justify-center rounded-full bg-destructive text-[8px] text-destructive-foreground group-hover:flex"
                  onClick={() => handleRemoveTag(t.id)}
                  title="移除标签"
                >
                  &times;
                </button>
              </span>
            ))}
            {availableTags.length > 0 && (
              <div className="flex items-center gap-1">
                <Select value={selectedTagId} onValueChange={(v) => v && setSelectedTagId(v)}>
                  <SelectTrigger className="h-7 w-28 text-xs">
                    <SelectValue placeholder="添加标签" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableTags.map((t) => (
                      <SelectItem key={t.id} value={String(t.id)}>
                        {t.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button size="sm" variant="outline" className="h-7 text-xs" onClick={handleAddTag}>
                  添加
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center gap-3 text-sm text-muted-foreground">
        <Badge variant="secondary">{link.source}</Badge>
        <span>
          状态:{" "}
          {analyzing ? (
            <span className="text-amber-600 font-medium">分析中...</span>
          ) : (
            link.status
          )}
        </span>
        {link.url && (
          <a href={link.url} target="_blank" rel="noreferrer" className="hover:underline">
            原文链接 &rarr;
          </a>
        )}
      </div>

      {analyzing && (
        <Card>
          <CardContent className="py-6 text-center text-sm text-muted-foreground">
            正在分析内容，请稍候...
          </CardContent>
        </Card>
      )}

      {!analyzing && link.error && (
        <Card className="border-destructive">
          <CardContent className="py-4 text-sm text-destructive">
            处理失败: {link.error}
          </CardContent>
        </Card>
      )}

      {!analyzing && link.status === "no_content" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">手动补充内容</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              自动提取失败，可以粘贴正文内容后重新分析
            </p>
            <textarea
              className="w-full min-h-[200px] rounded-md border border-input bg-transparent px-3 py-2 text-sm"
              placeholder="在此粘贴内容..."
              value={manualContent}
              onChange={(e) => setManualContent(e.target.value)}
            />
            <div className="flex gap-2">
              <Button disabled={saving || !manualContent.trim()} onClick={handleSaveManualContent}>
                {saving ? "保存中..." : "保存并分析"}
              </Button>
              <Button variant="outline" onClick={handleAnalyze}>
                重新抓取
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {link.summary && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">摘要</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{link.summary}</p>
          </CardContent>
        </Card>
      )}

      {link.content && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">正文</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap text-sm leading-relaxed">{link.content}</pre>
          </CardContent>
        </Card>
      )}

      <Button variant="destructive" disabled={deleting} onClick={handleDelete}>
        删除
      </Button>
    </div>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, type LinkResponse, type TagResponse } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
  const [deleting, setDeleting] = useState(false);
  const [selectedTagId, setSelectedTagId] = useState("");
  const [newTagName, setNewTagName] = useState("");

  const linkId = Number(params.id);

  const load = useCallback(async () => {
    const [l, tags] = await Promise.all([
      api.getLink(linkId),
      api.listTags(),
    ]);
    setLink(l);
    setAllTags(tags);
    setLoading(false);
  }, [linkId]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleAddTag() {
    if (!link) return;
    const currentIds = link.tags.map((t) => t.id);

    if (selectedTagId) {
      await api.updateLinkTags(link.id, [...currentIds, Number(selectedTagId)]);
      setSelectedTagId("");
    }

    const tagName = newTagName.trim();
    if (tagName) {
      // 先查是否已有同名标签
      const existing = allTags.find((t) => t.name === tagName);
      if (existing) {
        if (!currentIds.includes(existing.id)) {
          await api.updateLinkTags(link.id, [...currentIds, existing.id]);
        }
      } else {
        try {
          const created = await api.createTag(tagName);
          await api.updateLinkTags(link.id, [...currentIds, created.id]);
        } catch {
          // 409 冲突：刷新标签列表后重试
          const tags = await api.listTags();
          setAllTags(tags);
          const match = tags.find((t) => t.name === tagName);
          if (match && !currentIds.includes(match.id)) {
            await api.updateLinkTags(link.id, [...currentIds, match.id]);
          }
        }
      }
      setNewTagName("");
    }

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

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">标签</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
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
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {availableTags.length > 0 && (
              <>
                <Select value={selectedTagId} onValueChange={(v) => v && setSelectedTagId(v)}>
                  <SelectTrigger className="h-8 w-32 text-xs">
                    <SelectValue placeholder="选择标签" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableTags.map((t) => (
                      <SelectItem key={t.id} value={String(t.id)}>
                        {t.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <span className="text-xs text-muted-foreground">或</span>
              </>
            )}
            <Input
              className="h-8 w-28 text-xs"
              placeholder="新建标签"
              value={newTagName}
              onChange={(e) => setNewTagName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddTag()}
            />
            <Button size="sm" variant="outline" className="h-8 text-xs" onClick={handleAddTag}>
              添加
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center gap-3 text-sm text-muted-foreground">
        <Badge variant="secondary">{link.source}</Badge>
        {link.url && (
          <a href={link.url} target="_blank" rel="noreferrer" className="hover:underline">
            原文链接 &rarr;
          </a>
        )}
      </div>

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
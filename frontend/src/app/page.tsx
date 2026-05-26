"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type LinkResponse, type TagResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LinkCard } from "@/components/link-card";

export default function DashboardPage() {
  const [tags, setTags] = useState<TagResponse[]>([]);
  const [recent, setRecent] = useState<LinkResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.listTags(), api.listLinks({ page_size: 10 })])
      .then(([t, l]) => {
        setTags(t);
        setRecent(l.items);
        setLoading(false);
      })
      .catch((e) => {
        setError(e instanceof Error ? e.message : "加载失败");
        setLoading(false);
      });
  }, []);

  const handleExportJson = useCallback(async () => {
    try {
      const resp = await fetch(api.getExportJsonUrl());
      if (!resp.ok) throw new Error("导出失败");
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `mindvault-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("导出失败：" + (e instanceof Error ? e.message : "未知错误"));
    }
  }, []);

  const handleExportMarkdown = useCallback(() => {
    window.open(api.getExportMarkdownUrl(), "_blank");
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">仪表盘</h1>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-1">
                <div className="h-3 w-16 animate-pulse rounded bg-muted" />
              </CardHeader>
              <CardContent>
                <div className="h-8 w-12 animate-pulse rounded bg-muted" />
              </CardContent>
            </Card>
          ))}
        </div>
        <section>
          <div className="h-5 w-24 animate-pulse rounded bg-muted mb-3" />
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Card key={i}>
                <CardContent className="py-4">
                  <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">{error}</p>
        <Button onClick={() => window.location.reload()}>重试</Button>
      </div>
    );
  }

  const totalLinks = tags.reduce((s, t) => s + t.link_count, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">仪表盘</h1>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleExportJson}>
            导出 JSON
          </Button>
          <Button variant="outline" size="sm" onClick={handleExportMarkdown}>
            导出 Markdown
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="text-sm text-muted-foreground">链接总数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{totalLinks}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="text-sm text-muted-foreground">标签数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{tags.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="text-sm text-muted-foreground">标签</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-1">
              {tags.slice(0, 6).map((t) => (
                <span key={t.id} className="text-xs bg-secondary px-1.5 py-0.5 rounded">
                  {t.name}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-3">最近添加</h2>
        <div className="space-y-3">
          {recent.map((link) => (
            <LinkCard key={link.id} link={link} />
          ))}
          {recent.length === 0 && (
            <p className="text-sm text-muted-foreground">暂无内容，去提交页面添加链接或文本。</p>
          )}
        </div>
      </section>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { api, type LinkResponse, type TagResponse } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LinkCard } from "@/components/link-card";

export default function DashboardPage() {
  const [tags, setTags] = useState<TagResponse[]>([]);
  const [recent, setRecent] = useState<LinkResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.listTags(), api.listLinks({ page_size: 10 })]).then(
      ([t, l]) => {
        setTags(t);
        setRecent(l.items);
        setLoading(false);
      },
    );
  }, []);

  if (loading) return <div className="text-center text-muted-foreground py-12">加载中...</div>;

  const totalLinks = tags.reduce((s, t) => s + t.link_count, 0);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">仪表盘</h1>

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

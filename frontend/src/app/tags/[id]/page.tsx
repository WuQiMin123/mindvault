"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, type LinkResponse, type TagResponse } from "@/lib/api";
import { LinkCard } from "@/components/link-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";

export default function TagDetailPage() {
  const params = useParams();
  const router = useRouter();
  const tagName = decodeURIComponent(params.id as string);

  const [tag, setTag] = useState<TagResponse | null>(null);
  const [links, setLinks] = useState<LinkResponse[]>([]);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.listTags().then(async (tags) => {
      const found = tags.find((t) => t.name === tagName);
      if (!found) return setLoading(false);
      setTag(found);
      const data = await api.getTagSummary(found.id);
      setLinks(data.links);
      setSummary(data.aggregate_summary);
      setLoading(false);
    });
  }, [tagName]);

  const filtered = search
    ? links.filter(
        (l) =>
          l.title.toLowerCase().includes(search.toLowerCase()) ||
          l.summary?.toLowerCase().includes(search.toLowerCase()),
      )
    : links;

  if (loading) return <div className="text-center text-muted-foreground py-12">加载中...</div>;
  if (!tag) return <div className="text-center text-muted-foreground py-12">标签不存在</div>;

  return (
    <div className="space-y-6">
      <button
        className="text-sm text-muted-foreground hover:underline cursor-pointer"
        onClick={() => router.push("/tags")}
      >
        &larr; 返回标签列表
      </button>

      <h1 className="text-2xl font-bold">{tag.name}</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">聚合摘要</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{summary}</p>
        </CardContent>
      </Card>

      <Input
        placeholder="在标签内搜索..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <div className="space-y-3">
        {filtered.map((link) => (
          <LinkCard key={link.id} link={link} />
        ))}
        {filtered.length === 0 && (
          <p className="text-sm text-muted-foreground">暂无内容</p>
        )}
      </div>
    </div>
  );
}

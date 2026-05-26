"use client";

import { useEffect, useState } from "react";
import { api, type LinkResponse, type TagResponse } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { LinkCard } from "@/components/link-card";
import { Pagination } from "@/components/pagination";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<LinkResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [tags, setTags] = useState<TagResponse[]>([]);
  const [selectedTag, setSelectedTag] = useState("");
  const [searched, setSearched] = useState(false);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    api.listTags().then(setTags);
  }, []);

  async function handleSearch(p?: number) {
    const pg = p ?? 1;
    setSearching(true);
    try {
      const res = await api.search({
        q,
        tag_ids: selectedTag,
        page: pg,
      });
      setResults(res.items);
      setTotal(res.total);
      setPage(pg);
      setSearched(true);
    } finally {
      setSearching(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">搜索</h1>

      <div className="flex gap-2">
        <Input
          placeholder="关键词..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          className="flex-1"
        />
        <Select value={selectedTag} onValueChange={(v) => v && setSelectedTag(v)}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="标签筛选" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">全部</SelectItem>
            {tags.map((t) => (
              <SelectItem key={t.id} value={String(t.id)}>
                {t.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-3">
        {searching ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-24 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        ) : (
          <>
            {results.map((link) => (
              <LinkCard key={link.id} link={link} />
            ))}
            {searched && results.length === 0 && (
              <p className="text-sm text-muted-foreground">未找到匹配内容</p>
            )}
          </>
        )}
      </div>

      <Pagination
        page={page}
        pageSize={20}
        total={total}
        onPageChange={(p) => handleSearch(p)}
      />
    </div>
  );
}

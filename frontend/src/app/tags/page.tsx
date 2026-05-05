"use client";

import { useEffect, useState } from "react";
import { api, type TagResponse } from "@/lib/api";
import { TagBadge } from "@/components/tag-badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export default function TagsPage() {
  const [tags, setTags] = useState<TagResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [newName, setNewName] = useState("");

  function load() {
    setLoading(true);
    api.listTags().then((t) => {
      setTags(t);
      setLoading(false);
    });
  }

  useEffect(load, []);

  async function handleCreate() {
    if (!newName.trim()) return;
    await api.createTag(newName.trim());
    setNewName("");
    load();
  }

  async function handleDelete(id: number) {
    await api.deleteTag(id);
    load();
  }

  if (loading) return <div className="text-center text-muted-foreground py-12">加载中...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">标签</h1>

        <Dialog>
          <DialogTrigger>新建标签</DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>新建标签</DialogTitle>
            </DialogHeader>
            <div className="flex gap-2">
              <Input
                placeholder="标签名"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleCreate()}
              />
              <Button onClick={handleCreate}>创建</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex flex-wrap gap-2">
        {tags.map((t) => (
          <div key={t.id} className="group relative">
            <TagBadge name={t.name} color={t.color} linkCount={t.link_count} />
            <button
              className="absolute -top-1.5 -right-1.5 hidden size-4 cursor-pointer items-center justify-center rounded-full bg-destructive text-[10px] text-destructive-foreground group-hover:flex"
              onClick={() => handleDelete(t.id)}
              title="删除"
            >
              &times;
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

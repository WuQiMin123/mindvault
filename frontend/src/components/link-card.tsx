import type { LinkResponse } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TagBadge } from "@/components/tag-badge";
import Link from "next/link";

const sourceLabels: Record<string, string> = {
  bilibili: "B站",
  zhihu: "知乎",
  manual: "手动",
  web: "网页",
};

export function LinkCard({ link }: { link: LinkResponse }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base leading-snug">
            {link.url ? (
              <a href={link.url} target="_blank" rel="noreferrer" className="hover:underline">
                {link.title}
              </a>
            ) : (
              link.title
            )}
          </CardTitle>
          <div className="flex shrink-0 gap-1">
            <Badge variant="secondary" className="text-[10px]">
              {sourceLabels[link.source] || link.source}
            </Badge>
            {link.status === "no_content" && (
              <Badge variant="destructive" className="text-[10px]">
                无内容
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-2 pb-3">
        {link.summary && (
          <p className="text-sm text-muted-foreground line-clamp-2">{link.summary}</p>
        )}
        <div className="flex flex-wrap gap-1">
          {link.tags.map((t) => (
            <TagBadge key={t.id} name={t.name} color={t.color} />
          ))}
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <Link href={`/links/${link.id}`} className="hover:underline">
            详情
          </Link>
          <span>{link.created_at?.slice(0, 10)}</span>
        </div>
      </CardContent>
    </Card>
  );
}

import { Badge } from "@/components/ui/badge";
import Link from "next/link";

interface TagBadgeProps {
  name: string;
  color?: string | null;
  linkCount?: number;
}

export function TagBadge({ name, color, linkCount }: TagBadgeProps) {
  return (
    <Link href={`/tags/${encodeURIComponent(name)}`}>
      <Badge
        variant="outline"
        className="cursor-pointer hover:bg-accent"
        style={color ? { borderColor: color, color } : undefined}
      >
        {name}
        {linkCount !== undefined && (
          <span className="ml-1 text-xs text-muted-foreground">({linkCount})</span>
        )}
      </Badge>
    </Link>
  );
}

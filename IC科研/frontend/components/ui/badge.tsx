import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-line bg-panel px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.12em] text-muted",
        className,
      )}
      {...props}
    />
  );
}


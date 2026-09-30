export function PlaceholderPage({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <h1 className="text-[22px] font-bold text-foreground">{title}</h1>
      <div className="mt-4 flex min-h-[240px] items-center justify-center rounded-lg border border-border bg-card p-[18px] text-[13.5px] font-medium text-muted-foreground shadow-sm">
        {description}
      </div>
    </div>
  );
}

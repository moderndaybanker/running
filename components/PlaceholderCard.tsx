export function PlaceholderCard({ title, message }: { title: string; message: string }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-panel/80 p-4 shadow-lg shadow-black/20">
      <h2 className="text-lg font-medium text-white">{title}</h2>
      <p className="mt-2 text-sm text-slate-300">{message}</p>
    </article>
  );
}

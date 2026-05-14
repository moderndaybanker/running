const metrics = ['Weekly Distance', 'Avg Pace', 'Runs This Week', 'Active Streak'];

export function MetricGrid() {
  return (
    <div className="grid grid-cols-2 gap-3">
      {metrics.map((metric) => (
        <div key={metric} className="rounded-2xl border border-white/10 bg-panel/80 p-3">
          <p className="text-xs uppercase tracking-wider text-slate-400">{metric}</p>
          <p className="mt-3 text-xl font-semibold text-slate-100">--</p>
        </div>
      ))}
    </div>
  );
}

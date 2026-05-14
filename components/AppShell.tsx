import { ReactNode } from 'react';
import { BottomNav } from './BottomNav';

export function AppShell({ title, children }: { title: string; children: ReactNode }) {
  return (
    <main className="mx-auto min-h-screen max-w-md bg-gradient-to-b from-slateDeep via-[#10192b] to-slateDeep px-4 pb-24 pt-6">
      <header className="mb-6 rounded-2xl border border-white/10 bg-panel/70 p-4 shadow-glow backdrop-blur">
        <p className="text-xs uppercase tracking-[0.24em] text-accentSoft">PaceLab</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">{title}</h1>
      </header>
      <section className="space-y-4">{children}</section>
      <BottomNav />
    </main>
  );
}

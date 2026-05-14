'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/add-run', label: 'Add Run' },
  { href: '/run-history', label: 'History' },
  { href: '/analytics', label: 'Analytics' },
  { href: '/goals', label: 'Goals' }
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-1/2 w-full max-w-md -translate-x-1/2 border-t border-white/10 bg-slateDeep/95 px-2 py-3 backdrop-blur">
      <ul className="grid grid-cols-5 gap-1">
        {navItems.map((item) => {
          const active = pathname === item.href;

          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`block rounded-xl px-2 py-2 text-center text-[11px] font-medium transition ${
                  active ? 'bg-accent/20 text-accentSoft' : 'text-slate-400 hover:text-slate-100'
                }`}
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

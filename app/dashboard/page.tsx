import { AppShell } from '@/components/AppShell';
import { MetricGrid } from '@/components/MetricGrid';
import { PlaceholderCard } from '@/components/PlaceholderCard';

export default function DashboardPage() {
  return (
    <AppShell title="Dashboard">
      <MetricGrid />
      <PlaceholderCard title="Today\'s Snapshot" message="Run summaries and smart highlights will appear here soon." />
    </AppShell>
  );
}

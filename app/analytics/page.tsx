import { AppShell } from '@/components/AppShell';
import { PlaceholderCard } from '@/components/PlaceholderCard';

export default function AnalyticsPage() {
  return (
    <AppShell title="Analytics">
      <PlaceholderCard
        title="Charts & Trends"
        message="Recharts visualizations for pace trends, cadence, and training load will live in this section."
      />
    </AppShell>
  );
}

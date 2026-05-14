import { AppShell } from '@/components/AppShell';
import { PlaceholderCard } from '@/components/PlaceholderCard';

export default function RunHistoryPage() {
  return (
    <AppShell title="Run History">
      <PlaceholderCard title="Recent Runs" message="Logged workouts will render in a filterable timeline here." />
    </AppShell>
  );
}

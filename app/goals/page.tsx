import { AppShell } from '@/components/AppShell';
import { PlaceholderCard } from '@/components/PlaceholderCard';

export default function GoalsPage() {
  return (
    <AppShell title="Goals">
      <PlaceholderCard title="Goal Planner" message="Set milestones, targets, and progress checkpoints from this page." />
    </AppShell>
  );
}

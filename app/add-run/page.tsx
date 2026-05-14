import { AppShell } from '@/components/AppShell';
import { PlaceholderCard } from '@/components/PlaceholderCard';

export default function AddRunPage() {
  return (
    <AppShell title="Add Run">
      <PlaceholderCard
        title="Run Entry Form"
        message="Form fields for distance, duration, route, and notes will be connected in a future backend pass."
      />
    </AppShell>
  );
}

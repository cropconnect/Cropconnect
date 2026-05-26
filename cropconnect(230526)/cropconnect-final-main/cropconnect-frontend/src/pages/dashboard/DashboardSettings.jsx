import DashboardPageContent from "../../components/dashboard/DashboardPageContent";
import { useDashboard } from "../../contexts/DashboardContext";

export default function DashboardSettings() {
  const ctx = useDashboard();
  // Lazy wrapper keeps settings/profile routes code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

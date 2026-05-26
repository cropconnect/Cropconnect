import DashboardPageContent from "../../components/dashboard/DashboardPageContent";
import { useDashboard } from "../../contexts/DashboardContext";

export default function DashboardHome() {
  const ctx = useDashboard();
  // Lazy wrapper keeps the overview route code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

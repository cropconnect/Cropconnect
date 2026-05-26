import DashboardPageContent from "../../components/dashboard/DashboardPageContent";
import { useDashboard } from "../../contexts/DashboardContext";

export default function DashboardPump() {
  const ctx = useDashboard();
  // Lazy wrapper keeps the pump route code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

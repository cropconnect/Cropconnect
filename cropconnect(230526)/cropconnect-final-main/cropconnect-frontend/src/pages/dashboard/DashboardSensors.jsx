import DashboardPageContent from "../../components/dashboard/DashboardPageContent";
import { useDashboard } from "../../contexts/DashboardContext";

export default function DashboardSensors() {
  const ctx = useDashboard();
  // Lazy wrapper keeps the sensors route code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

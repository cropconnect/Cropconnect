import DashboardPageContent from "../../components/dashboard/DashboardPageContent";
import { useDashboard } from "../../contexts/DashboardContext";

export default function DashboardWeather() {
  const ctx = useDashboard();
  // Lazy wrapper keeps the weather route code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

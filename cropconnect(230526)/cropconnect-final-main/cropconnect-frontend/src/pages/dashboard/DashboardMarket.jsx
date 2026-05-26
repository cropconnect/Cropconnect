import DashboardPageContent from "../../components/dashboard/DashboardPageContent";
import { useDashboard } from "../../contexts/DashboardContext";

export default function DashboardMarket() {
  const ctx = useDashboard();
  // Lazy wrapper keeps the market route code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

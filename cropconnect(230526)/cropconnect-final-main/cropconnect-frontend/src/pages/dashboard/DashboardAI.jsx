import DashboardPageContent from "../../components/dashboard/DashboardPageContent";
import { useDashboard } from "../../contexts/DashboardContext";

export default function DashboardAI() {
  const ctx = useDashboard();
  // Lazy wrapper keeps AI and planner routes code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

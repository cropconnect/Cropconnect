import DashboardPageContent from "../../components/dashboard/DashboardPageContent";

export default function DashboardAI({ ctx }) {
  // Lazy wrapper keeps AI and planner routes code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

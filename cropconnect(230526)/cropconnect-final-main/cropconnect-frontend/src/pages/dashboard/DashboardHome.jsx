import DashboardPageContent from "../../components/dashboard/DashboardPageContent";

export default function DashboardHome({ ctx }) {
  // Lazy wrapper keeps the overview route code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

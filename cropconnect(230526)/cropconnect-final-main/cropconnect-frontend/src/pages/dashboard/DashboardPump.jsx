import DashboardPageContent from "../../components/dashboard/DashboardPageContent";

export default function DashboardPump({ ctx }) {
  // Lazy wrapper keeps the pump route code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

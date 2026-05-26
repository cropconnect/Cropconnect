import DashboardPageContent from "../../components/dashboard/DashboardPageContent";

export default function DashboardSettings({ ctx }) {
  // Lazy wrapper keeps settings/profile routes code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

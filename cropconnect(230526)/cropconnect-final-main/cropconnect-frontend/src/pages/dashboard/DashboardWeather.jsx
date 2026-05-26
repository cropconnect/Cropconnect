import DashboardPageContent from "../../components/dashboard/DashboardPageContent";

export default function DashboardWeather({ ctx }) {
  // Lazy wrapper keeps the weather route code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

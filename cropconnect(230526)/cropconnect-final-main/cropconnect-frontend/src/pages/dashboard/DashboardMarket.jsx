import DashboardPageContent from "../../components/dashboard/DashboardPageContent";

export default function DashboardMarket({ ctx }) {
  // Lazy wrapper keeps the market route code-split without changing dashboard behavior.
  return <DashboardPageContent ctx={ctx} />;
}

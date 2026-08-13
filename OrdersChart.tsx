import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js";
import { Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

export const CHART_PALETTE = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#0ea5e9", "#a855f7"];

export default function OrdersChart({
  labels,
  values,
  dark,
  centerLabel,
  centerValue,
  onSliceClick,
}: {
  labels: string[];
  values: number[];
  dark: boolean;
  centerLabel?: string;
  centerValue?: string;
  onSliceClick?: (index: number) => void;
}) {
  const data = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: CHART_PALETTE.slice(0, labels.length),
        borderWidth: dark ? 3 : 2,
        borderColor: dark ? "#0f172a" : "#ffffff",
        hoverOffset: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "68%",
    plugins: {
      legend: {
        position: "bottom" as const,
        labels: {
          color: dark ? "#cbd5e1" : "#475569",
          padding: 14,
          usePointStyle: true,
          pointStyle: "circle" as const,
          boxWidth: 8,
          font: { size: 11, weight: 500 },
        },
      },
      tooltip: {
        backgroundColor: dark ? "#1e293b" : "#0f172a",
        padding: 12,
        cornerRadius: 10,
        displayColors: true,
        boxPadding: 4,
        callbacks: {
          label: (ctx: { label: string; parsed: number }) =>
            ` ${ctx.label}: ${ctx.parsed}%`,
        },
      },
    },
    onClick: (_e: unknown, elements: { index: number }[]) => {
      if (onSliceClick && elements.length > 0) onSliceClick(elements[0].index);
    },
  };

  return (
    <div className="relative h-64 w-full">
      <Doughnut data={data} options={options} />
      {centerLabel && (
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center pb-8">
          <span className="text-[11px] font-medium uppercase tracking-wide text-slate-400 dark:text-slate-500">
            {centerLabel}
          </span>
          <span className="text-xl font-bold text-slate-900 dark:text-white">{centerValue}</span>
        </div>
      )}
    </div>
  );
}

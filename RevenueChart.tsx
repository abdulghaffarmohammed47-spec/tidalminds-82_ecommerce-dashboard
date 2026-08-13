import {
  Chart as ChartJS,
  CategoryScale,
  Filler,
  Legend,
  LinearScale,
  type ChartData,
  type ChartOptions,
  type ScriptableContext,
  BarElement,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js";
import { Bar as BarChart, Line as LineChart } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  Filler
);

export type ChartType = "line" | "area" | "bar";

export default function RevenueChart({
  labels,
  values,
  dark,
  type = "line",
  onPointClick,
  height = 280,
  legendLabel = "Revenue",
}: {
  labels: string[];
  values: number[];
  dark: boolean;
  type?: ChartType;
  onPointClick?: (index: number) => void;
  height?: number;
  legendLabel?: string;
}) {
  const tickColor = dark ? "#94a3b8" : "#64748b";
  const gridColor = dark ? "rgba(148,163,184,0.12)" : "rgba(100,116,139,0.15)";

  const data: ChartData<"line" | "bar"> = {
    labels,
    datasets: [
      {
        label: legendLabel,
        data: values,
        borderColor: "#6366f1",
        borderWidth: 2.5,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 6,
        pointBackgroundColor: "#6366f1",
        pointBorderColor: dark ? "#0f172a" : "#ffffff",
        pointBorderWidth: 2,
        fill: type === "area",
        backgroundColor:
          type === "bar"
            ? "rgba(99,102,241,0.85)"
            : (context: ScriptableContext<"line">) => {
                const { ctx, chartArea } = context.chart;
                if (!chartArea) return "rgba(99,102,241,0.15)";
                const g = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                g.addColorStop(0, "rgba(99,102,241,0.32)");
                g.addColorStop(1, "rgba(99,102,241,0.02)");
                return g;
              },
        borderRadius: 8,
        maxBarThickness: 44,
      },
    ],
  };

  const options: ChartOptions<"line" | "bar"> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: dark ? "#1e293b" : "#0f172a",
        titleColor: "#fff",
        bodyColor: "#e2e8f0",
        padding: 12,
        cornerRadius: 10,
        displayColors: false,
        callbacks: {
          label: (ctx) => ` ${ctx.dataset.label}: $${Number(ctx.raw).toLocaleString()}`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        border: { display: false },
        ticks: { color: tickColor, font: { size: 11, weight: 500 } },
      },
      y: {
        grid: { color: gridColor },
        border: { display: false },
        ticks: {
          color: tickColor,
          font: { size: 11 },
          callback: (v) => `$${(Number(v) / 1000).toFixed(0)}k`,
        },
      },
    },
    onClick: (_e, elements) => {
      if (onPointClick && elements.length > 0) onPointClick(elements[0].index);
    },
  };

  return (
    <div style={{ height }} className="relative w-full">
      {type === "bar" ? (
        <BarChart data={data as ChartData<"bar">} options={options as ChartOptions<"bar">} />
      ) : (
        <LineChart data={data as ChartData<"line">} options={options as ChartOptions<"line">} />
      )}
    </div>
  );
}

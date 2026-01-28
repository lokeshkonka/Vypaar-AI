import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";
import CardComponent from "./CardComponent";

interface GraphDataPoint {
  day: string;
  forecast: number;
  actual?: number;
}

interface GraphComponentProps {
  title: string;
  data: GraphDataPoint[];
}

export default function GraphComponent({
  title,
  data,
}: GraphComponentProps) {
  // Ensure we have data, otherwise show placeholder
  if (!data || data.length === 0) {
    return (
      <CardComponent title={title}>
        <div className="h-64 sm:h-72 flex items-center justify-center text-soft">
          <p>No data available</p>
        </div>
      </CardComponent>
    );
  }

  return (
    <CardComponent title={title}>
      <div className="h-64 sm:h-72 w-full" style={{ minHeight: "200px" }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
          >
            {/* Grid */}
            <CartesianGrid
              stroke="var(--border)"
              strokeDasharray="3 3"
            />

            {/* X Axis */}
            <XAxis
              dataKey="day"
              tick={{
                fill: "var(--text-soft)",
                fontSize: 12,
              }}
              axisLine={{ stroke: "var(--border)" }}
              tickLine={false}
            />

            {/* Y Axis */}
            <YAxis
              tick={{
                fill: "var(--text-soft)",
                fontSize: 12,
              }}
              axisLine={false}
              tickLine={false}
            />

            {/* Tooltip */}
            <Tooltip
              contentStyle={{
                background: "var(--panel)",
                border: "1px solid var(--border)",
                borderRadius: 0,
                color: "var(--text-main)",
                fontSize: 13,
              }}
              labelStyle={{
                color: "var(--text-soft)",
                marginBottom: 4,
              }}
            />

            {/* Legend */}
            <Legend
              wrapperStyle={{
                fontSize: 12,
                color: "var(--text-soft)",
              }}
            />

            {/* Past Sales (DOTTED) */}
            <Line
              type="monotone"
              dataKey="actual"
              name="Past Sales"
              stroke="var(--text-soft)"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={false}
              animationDuration={600}
            />

            {/* Forecast (SOLID) */}
            <Line
              type="monotone"
              dataKey="forecast"
              name="Forecast"
              stroke={`rgb(var(--emerald-main))`}
              strokeWidth={3}
              dot={false}
              activeDot={{
                r: 6,
                strokeWidth: 2,
                stroke: `rgb(var(--emerald-main))`,
                fill: "var(--bg-main)",
              }}
              animationDuration={900}
              animationEasing="ease-out"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </CardComponent>
  );
}

import TableComponent from "../ui/TableComponent";
import CardComponent from "../ui/CardComponent";
import { useNavigate } from "react-router-dom";
import { useInventory } from "../../context/InventoryContext";
import InventoryFilters from "./InventoryFilters";

export default function YourStock() {
  const { inventory, isUpdating } = useInventory();
  const navigate = useNavigate();

  return (
    <div className="space-y-4">
      {/* TOP ROW: Filters + Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Filters */}
        <div className="lg:col-span-2">
          <InventoryFilters />
        </div>
        {/* Actions */}
<CardComponent title="Forecast Actions">
  <p className="text-sm text-soft leading-relaxed mb-2">
    Modify your forecast configuration such as time horizon (7 or 14 days),
  </p>

  <button
    onClick={() => navigate("/dashboard/selector")}
    className="
      w-full py-3 text-sm font-semibold
      bg-emerald-600 dark:text-white text-black hover:bg-emerald-700 hover:shadow-[0_12px_30px_rgba(16,185,129,0.35)] active:scale-[0.98]
      transition
    "
  >
    Change Forecast
  </button>
</CardComponent>

      </div>

      {/* BOTTOM ROW: Table */}
      <TableComponent
        title="Your Stocks"
        loading={isUpdating}
        columns={[
          { key: "product", label: "Product" },

          {
            key: "current",
            label: "Your Stock",
            align: "right",
          },

          {
            key: "suggested",
            label: "Suggested",
            align: "right",
          },

          {
            key: "suggested",
            label: "Buffer",
            align: "right",
            render: (_, row) => {
              const buffer = row.suggested - row.current;
              return (
                <span
                  className={
                    buffer > 0
                      ? "text-emerald-600"
                      : "text-orange-500"
                  }
                >
                  {buffer > 0 ? `+${buffer}` : buffer}
                </span>
              );
            },
          },

          {
            key: "risk",
            label: "Risk",
            render: (value) => {
              const color =
                value === "Low"
                  ? "text-emerald-600"
                  : value === "Medium"
                  ? "text-yellow-600"
                  : "text-red-600";

              return (
                <span className={`font-medium ${color}`}>
                  {value}
                </span>
              );
            },
          },
        ]}
        data={inventory}
      />
    </div>
  );
}

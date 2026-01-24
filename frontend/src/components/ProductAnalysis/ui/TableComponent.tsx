interface TableColumn<T> {
  key: keyof T;
  label: string;
  align?: "left" | "right" | "center";
  render?: (value: T[keyof T], row: T) => React.ReactNode;
}

interface TableComponentProps<T> {
  title?: string;
  icon?: React.ReactNode;
  columns: TableColumn<T>[];
  data: T[];
}

export default function TableComponent<T>({
  title,
  icon,
  columns,
  data,
}: TableComponentProps<T>) {
  return (
    <div
      className="
        glass-card
        p-6 sm:p-7
        rounded-none
        transition-all duration-200
      "
    >
      {/* Header */}
      {title && (
        <div className="flex items-center gap-2 mb-5">
          {icon && (
            <span className="text-[rgb(var(--emerald-main))]">
              {icon}
            </span>
          )}
          <h3
            className="
              text-base sm:text-lg
              font-semibold
              tracking-wide
              uppercase
              text-main
            "
          >
            {title}
          </h3>
        </div>
      )}

      {/* Table wrapper with outer border */}
      <div
        className="overflow-x-auto"
        style={{ border: "1px solid var(--border)" }}
      >
        <table className="w-full border-collapse">
          <thead>
            <tr>
              {columns.map((col, index) => (
                <th
                  key={String(col.key)}
                  className="
                    px-3 py-2.5
                    text-sm sm:text-[0.95rem]
                    font-semibold
                    uppercase
                    tracking-wide
                    text-soft
                    border-b
                  "
                  style={{
                    borderColor: "var(--border)",
                    textAlign: col.align ?? "left",
                    borderRight:
                      index !== columns.length - 1
                        ? "1px solid var(--border)"
                        : undefined,
                  }}
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {data.map((row, i) => (
              <tr
                key={i}
                className="
                  transition-colors
                  hover:bg-[rgba(var(--glass-white),0.18)]
                "
              >
                {columns.map((col, index) => (
                  <td
                    key={String(col.key)}
                    className="
                      px-3 py-3.5
                      text-base
                      font-medium
                      text-main
                      border-b
                    "
                    style={{
                      borderColor: "var(--border)",
                      textAlign: col.align ?? "left",
                      borderRight:
                        index !== columns.length - 1
                          ? "1px solid var(--border)"
                          : undefined,
                    }}
                  >
                    {col.render
                      ? col.render(row[col.key], row)
                      : String(row[col.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

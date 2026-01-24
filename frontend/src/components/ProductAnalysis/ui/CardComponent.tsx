// src/components/product-analysis/ui/CardComponent.tsx

export default function CardComponent({
  title,
  icon,
  children,
}: {
  title?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div
      className="
        glass-card
        p-6 sm:p-7
        flex flex-col
        space-y-4
        rounded-none

        transition-all duration-200 ease-out
        hover:-translate-y-[1px]
        hover:shadow-[0_8px_24px_rgba(0,0,0,0.06)]
        dark:hover:shadow-[0_8px_24px_rgba(0,0,0,0.35)]
      "
    >
      {/* Header: Icon + Title inline */}
      {title && (
        <div className="flex items-center gap-2">
          {icon && (
            <span
              className="
                flex items-center
                text-[rgb(var(--emerald-main))]
              "
            >
              {icon}
            </span>
          )}

          <h3
            className="
              text-sm sm:text-base
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

      {/* Divider */}
      <div
        className="h-px w-10"
        style={{ backgroundColor: "var(--border)" }}
      />

      {/* Main content */}
      <div
        className="
          text-base sm:text-lg
          font-medium
          text-main
        "
      >
        {children}
      </div>
    </div>
  );
}

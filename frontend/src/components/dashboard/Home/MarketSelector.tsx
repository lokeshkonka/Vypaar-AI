import { MapPin } from "lucide-react";
import { markets } from "../../../data/dummyData";
import { useForecast } from "../../../context/ForecastContext";
const inputBase =
  "w-full h-12 rounded-xl px-4 text-sm transition-colors " +
  // Light mode
  "bg-black border border-gray-300 " +
  "hover:border-gray-400 " +
  // Dark mode
  "dark:bg-white/5 dark:border-white/10  " +
  // Focus
  "focus:outline-none focus:ring-2 focus:ring-emerald-400/40 focus:border-emerald-400 " +
  // Disabled
  "disabled:opacity-60 disabled:cursor-not-allowed";



export default function MarketSelector() {
  const { selection, setSelection } = useForecast();

  const states = Array.from(
    new Set(markets.map((m) => m.state))
  );

  const cities = Array.from(
    new Set(
      markets
        .filter((m) => m.state === selection.state)
        .map((m) => m.city)
    )
  );

  const marketTypes = Array.from(
    new Set(
      markets
        .filter(
          (m) =>
            m.state === selection.state &&
            m.city === selection.city
        )
        .map((m) => m.type)
    )
  );

  const filteredMarkets = markets.filter(
    (m) =>
      m.state === selection.state &&
      m.city === selection.city &&
      m.type === selection.marketType
  );

  return (
    <div className="glass-card p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center gap-2">
        <MapPin className="w-5 h-5 text-emerald-600" />
        <h3 className="font-medium ">
          Market Configuration
        </h3>
      </div>

      {/* State */}
      <select
        className={inputBase}
        value={selection.state || ""}
        onChange={(e) =>
          setSelection({
            state: e.target.value,
            city: undefined,
            marketType: undefined,
            market: undefined,
          })
        }
      >
        <option value="">Select State</option>
        {states.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>

      {/* City */}
      <select
        className={inputBase}
        value={selection.city || ""}
        disabled={!selection.state}
        onChange={(e) =>
          setSelection({
            city: e.target.value,
            marketType: undefined,
            market: undefined,
          })
        }
      >
        <option value="">Select City</option>
        {cities.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      {/* Market Type */}
      <select
        className={inputBase}
        value={selection.marketType || ""}
        disabled={!selection.city}
        onChange={(e) =>
          setSelection({
            marketType: e.target.value,
            market: undefined,
          })
        }
      >
        <option value="">Select Market Type</option>
        {marketTypes.map((t) => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>

      {/* Market */}
      <select
        className={inputBase}
        value={selection.market || ""}
        disabled={!selection.marketType}
        onChange={(e) =>
          setSelection({
            market: e.target.value,
          })
        }
      >
        <option value="">Select Market</option>
        {filteredMarkets.map((m) => (
          <option key={m.id} value={m.name}>
            {m.name}
          </option>
        ))}
      </select>
    </div>
  );
}

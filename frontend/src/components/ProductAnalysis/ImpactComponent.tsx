// src/components/product-analysis/ImpactComponent.tsx
import { FiCalendar, FiCloudRain } from "react-icons/fi";
import CardComponent from "./ui/CardComponent";
import { useContextAnalysis } from "../../context/ContextAnalysis";

export default function ImpactComponent() {
  const { impactData } = useContextAnalysis();

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {/* Festival Impact */}
      <CardComponent
        title="Festival Impact"
        icon={<FiCalendar size={16} />}
      >
        <div className="space-y-1">
          <p className="text-soft text-sm">
            {impactData.festival}
          </p>
          <p className="text-main text-base font-medium">
            {impactData.festivalImpact}
          </p>
        </div>
      </CardComponent>

      {/* Weather Impact */}
      <CardComponent
        title="Weather Impact"
        icon={<FiCloudRain size={16} />}
      >
        <p className="text-main text-base font-medium leading-relaxed">
          {impactData.weather}
        </p>
      </CardComponent>
    </div>
  );
}

import { ChevronRight } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

const labelMap: Record<string, string> = {
  upload: "Upload",
  processing: "Processing",
  dashboard: "Dashboard",
  "fraud-details": "Fraud Details",
  explainability: "Explainability",
  chatbot: "AI Chatbot",
  reports: "AI Report",
  settings: "Settings",
};

export function Breadcrumbs() {
  const location = useLocation();
  const segments = location.pathname.split("/").filter(Boolean);

  return (
    <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
      <Link to="/" className="hover:text-foreground">
        Home
      </Link>
      {segments.map((segment, index) => {
        const href = `/${segments.slice(0, index + 1).join("/")}`;
        const isLast = index === segments.length - 1;
        return (
          <div key={href} className="flex items-center gap-2">
            <ChevronRight className="h-3.5 w-3.5" />
            {isLast ? (
              <span className="text-foreground">{labelMap[segment] ?? segment}</span>
            ) : (
              <Link to={href} className="hover:text-foreground">
                {labelMap[segment] ?? segment}
              </Link>
            )}
          </div>
        );
      })}
    </div>
  );
}

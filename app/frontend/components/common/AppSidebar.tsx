import { Link, useLocation } from "react-router-dom";
import { PanelLeftClose, ShieldCheck } from "lucide-react";
import { appNavigation } from "@/utils/constants";
import { cn } from "@/utils/cn";
import { Button } from "@/components/ui/button";

interface AppSidebarProps {
  onClose?: () => void;
}

export function AppSidebar({ onClose }: AppSidebarProps) {
  const location = useLocation();

  return (
    <aside className="flex h-full w-full flex-col gap-6 rounded-r-3xl border-r border-border/80 bg-card/85 px-5 py-6 shadow-panel backdrop-blur-xl">
      <div className="flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Workspace</p>
            <p className="text-sm font-semibold">Fraud Analysis</p>
          </div>
        </Link>

        {onClose ? (
          <Button variant="ghost" size="icon" onClick={onClose} className="lg:hidden">
            <PanelLeftClose className="h-4 w-4" />
          </Button>
        ) : null}
      </div>

      <div className="rounded-2xl border border-border/70 bg-secondary/50 p-4">
        <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Current Scope</p>
        <p className="mt-2 text-sm leading-6 text-foreground/90">
          Dataset-driven fraud detection workspace with analytics, explainability, reporting, and
          guided AI Q&A.
        </p>
      </div>

      <nav className="flex flex-1 flex-col gap-1.5">
        {appNavigation.map((item) => {
          const isActive = location.pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              to={item.href}
              className={cn(
                "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition",
                isActive
                  ? "bg-primary text-primary-foreground shadow-soft"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/8 p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-emerald-700 dark:text-emerald-300">
          Security Posture
        </p>
        <p className="mt-2 text-sm text-foreground/90">
          Encryption, validation gates, and audit-friendly explainability are surfaced throughout
          the workflow.
        </p>
      </div>
    </aside>
  );
}

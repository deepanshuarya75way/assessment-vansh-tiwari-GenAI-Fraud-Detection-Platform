import { useState } from "react";
import { Menu } from "lucide-react";
import { Outlet } from "react-router-dom";
import { AppSidebar } from "@/components/common/AppSidebar";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { ThemeSwitch } from "@/components/common/ThemeSwitch";
import { Button } from "@/components/ui/button";

export function DashboardLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[280px_minmax(0,1fr)]">
      <div className="hidden lg:block">
        <div className="sticky top-0 h-screen p-4">
          <AppSidebar />
        </div>
      </div>

      {isSidebarOpen ? (
        <div className="fixed inset-0 z-50 bg-slate-950/40 lg:hidden" onClick={() => setIsSidebarOpen(false)}>
          <div className="h-full max-w-[320px]" onClick={(event) => event.stopPropagation()}>
            <AppSidebar onClose={() => setIsSidebarOpen(false)} />
          </div>
        </div>
      ) : null}

      <div className="flex min-h-screen flex-col">
        <header className="sticky top-0 z-30 border-b border-border/70 bg-background/85 backdrop-blur-xl">
          <div className="flex items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-3">
              <Button variant="outline" size="icon" onClick={() => setIsSidebarOpen(true)} className="lg:hidden">
                <Menu className="h-4 w-4" />
              </Button>
              <div>
                <Breadcrumbs />
                <p className="mt-2 text-xs uppercase tracking-[0.24em] text-muted-foreground">
                  AI-Powered Financial Fraud Detection
                </p>
              </div>
            </div>
            <ThemeSwitch />
          </div>
        </header>

        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <div className="mx-auto w-full max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

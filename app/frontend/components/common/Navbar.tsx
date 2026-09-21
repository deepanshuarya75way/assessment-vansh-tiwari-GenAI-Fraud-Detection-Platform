import { Link } from "react-router-dom";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { ThemeSwitch } from "@/components/common/ThemeSwitch";
import { Button } from "@/components/ui/button";

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-soft">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
              IBM Internship Project
            </p>
            <p className="text-sm font-semibold">GenAI Fraud Platform</p>
          </div>
        </Link>

        <div className="hidden items-center gap-2 md:flex">
          <Link to="/upload">
            <Button variant="ghost">Upload Data</Button>
          </Link>
          <Link to="/dashboard">
            <Button>
              Open Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <ThemeSwitch />
        </div>

        <div className="md:hidden">
          <ThemeSwitch />
        </div>
      </div>
    </header>
  );
}

import { Outlet } from "react-router-dom";
import { Navbar } from "@/components/common/Navbar";

export function PublicLayout() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main>
        <Outlet />
      </main>
    </div>
  );
}

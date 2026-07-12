import { Outlet } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { CommandPalette } from "./command-palette";
import { useAppStore } from "@/store";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";

export function Layout() {
  const { sidebarOpen } = useAppStore();

  return (
    <div className="relative min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Mobile Sidebar (Sheet overlay) */}
      <div className="lg:hidden">
        <Sheet>
          <SheetTrigger asChild>
            <div className="fixed left-0 top-0 z-40 h-0 w-0" />
          </SheetTrigger>
          <SheetContent side="left" className="w-[280px] p-0">
            <Sidebar />
          </SheetContent>
        </Sheet>
      </div>

      {/* Header */}
      <Header />

      {/* Main Content */}
      <main
        className={cn(
          "min-h-screen pt-16 transition-all duration-300",
          sidebarOpen ? "lg:ml-[280px]" : "lg:ml-[72px]"
        )}
      >
        <div className="p-6">
          <Outlet />
        </div>
      </main>

      {/* Command Palette */}
      <CommandPalette />
    </div>
  );
}

export default Layout;

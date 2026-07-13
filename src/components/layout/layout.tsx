'use client'

import { useEffect } from "react";
import { cn } from "@/lib/utils";
import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { CommandPalette } from "./command-palette";
import { useAppStore } from "@/store";
import {
  Sheet,
  SheetContent,
} from "@/components/ui/sheet";

export function Layout({ children }: { children: React.ReactNode }) {
  const { sidebarOpen, toggleSidebar } = useAppStore();

  return (
    <div className="relative min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Mobile Sidebar (Sheet overlay) */}
      <div className="lg:hidden">
        <Sheet open={sidebarOpen} onOpenChange={toggleSidebar}>
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
          {children}
        </div>
      </main>

      {/* Command Palette */}
      <CommandPalette />
    </div>
  );
}

export default Layout;

import { useLocation, Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { ChevronRight, Home } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  className?: string;
}

const pathLabelMap: Record<string, string> = {
  dashboard: "Dashboard",
  etablissements: "Établissements",
  utilisateurs: "Utilisateurs",
  patients: "Patients",
  "cas-cliniques": "Cas Cliniques",
  "historique-traitements": "Historique des Traitements",
  statistiques: "Tableau de Bord Stats",
  chercheurs: "Chercheurs",
  synchronisation: "Synchronisation",
  parametres: "Paramètres",
  audit: "Journal d'Audit",
  profil: "Profil",
  notifications: "Notifications",
};

function generateBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split("/").filter(Boolean);
  const crumbs: BreadcrumbItem[] = [];

  let accumulatedPath = "";

  for (let i = 0; i < segments.length; i++) {
    accumulatedPath += `/${segments[i]}`;
    const isLast = i === segments.length - 1;

    crumbs.push({
      label:
        pathLabelMap[segments[i]] ||
        segments[i].charAt(0).toUpperCase() + segments[i].slice(1),
      href: isLast ? undefined : accumulatedPath,
    });
  }

  return crumbs;
}

export function Breadcrumbs({ items, className }: BreadcrumbsProps) {
  const location = useLocation();
  const breadcrumbs = items ?? generateBreadcrumbs(location.pathname);

  return (
    <nav
      className={cn(
        "flex items-center gap-1 text-sm text-muted-foreground",
        className
      )}
      aria-label="Fil d'Ariane"
    >
      <Link
        to="/"
        className="flex items-center gap-1 rounded-md px-1.5 py-0.5 transition-colors hover:text-foreground"
      >
        <Home className="h-3.5 w-3.5" />
      </Link>

      {breadcrumbs.map((crumb, index) => (
        <div key={index} className="flex items-center gap-1">
          <ChevronRight className="h-3.5 w-3.5 shrink-0 text-muted-foreground/50" />
          {crumb.href ? (
            <Link
              to={crumb.href}
              className="rounded-md px-1.5 py-0.5 transition-colors hover:text-foreground"
            >
              {crumb.label}
            </Link>
          ) : (
            <span className="px-1.5 font-medium text-foreground">
              {crumb.label}
            </span>
          )}
        </div>
      ))}
    </nav>
  );
}

export default Breadcrumbs;

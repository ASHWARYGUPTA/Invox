import AnimatedListItemUse from "@/components/AnimatedListItemUse";
import { AppSidebar } from "@/components/app-sidebar";
import FileUploadForm from "@/components/FileUploader";
import { SectionCards } from "@/components/section-cards";

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { DialogDemo } from "@/components/UploadDialog";
import { getServerSession } from "next-auth";
import { authOptions } from "../api/auth/[...nextauth]/route";
import DashboardContent from "./DashboardContent";
export default function Page() {
  const session = getServerSession(authOptions);
  if (!session) {
    return <>Unauthenticated</>;
  }
  const handleExportCSV = () => {
    // Add CSV export logic here
    console.log("Exporting as CSV...");
  };

  const handleExportJSON = () => {
    // Add JSON export logic here
    console.log("Exporting as JSON...");
  };

  return <DashboardContent />;
}

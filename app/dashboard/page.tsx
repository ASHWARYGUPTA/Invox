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

export default function Page() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator
              orientation="vertical"
              className="mr-2 data-[orientation=vertical]:h-4"
            />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink href="#">
                    <BreadcrumbPage>Dashboard</BreadcrumbPage>
                  </BreadcrumbLink>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          <div className="absolute top-0 right-0 m-3">
            <Button className="top-0 right-0">Upload Invoice</Button>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <div className="grid auto-rows-min gap-4 md:grid-cols-3 mb-4">
            <div className="">
              <SectionCards />
            </div>
            <div className="">
              <SectionCards />
            </div>
            <div className="">
              <SectionCards />
            </div>
          </div>
          {/* <div className="h-[100px] bg-muted rounded-3xl">
            {/* <FileUploadForm /> */}
          {/* </div> */}
          <div className="bg-muted/50 min-h-[100vh] flex-1 rounded-xl md:min-h-min">
            <div className="m-5 ">
              Invoice Overview
              <div className="flex justify-between items-center mx-25 mt-2">
                <div className="text-b">Invoice ID</div>
                <div className="text-b">Client Name</div>
                <div className="text-b">Date</div>
                <div className="text-b">Amount</div>
                <div className="text-b">Due Date</div>
                <div className="text-b">Status</div>
              </div>
              <div>
                <AnimatedListItemUse />
              </div>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}

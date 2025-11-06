"use client";
import AnimatedList from "./AnimatedList";
import axios from "axios";
import { useSession } from "next-auth/react";
import { useEffect, useState } from "react";
import { Button } from "./ui/button";

interface Invoice {
  invoiceNumber: string;
  invoiceDate: string;
  dueDate: string;
  amountPayable: string;
  currency: string;
  vendorName: string;
  customerName: string;
  ConfidenceScore: string;
}

// const items = [
//   {
//     invoiceNumber: "INV-001",
//     invoiceDate: "2025-10-12",
//     dueDate: "2025-11-12",
//     amountPayable: "1200",
//     currency: "USD",
//     vendorName: "Visionware Inc.",
//     customerName: "NeoTech Systems",
//     ConfidenceScore: "98%",
//   },
//   {
//     invoiceNumber: "INV-002",
//     invoiceDate: "2025-10-15",
//     dueDate: "2025-11-15",
//     amountPayable: "980",
//     currency: "USD",
//     vendorName: "TechNova Solutions",
//     customerName: "Orion Analytics",
//     ConfidenceScore: "95%",
//   },
//   {
//     invoiceNumber: "INV-003",
//     invoiceDate: "2025-10-20",
//     dueDate: "2025-11-20",
//     amountPayable: "2450",
//     currency: "EUR",
//     vendorName: "NextGen AI Labs",
//     customerName: "DataVerse Pvt Ltd",
//     ConfidenceScore: "92%",
//   },
//   {
//     invoiceNumber: "INV-003",
//     invoiceDate: "2025-10-20",
//     dueDate: "2025-11-20",
//     amountPayable: "2450",
//     currency: "EUR",
//     vendorName: "NextGen AI Labs",
//     customerName: "DataVerse Pvt Ltd",
//     ConfidenceScore: "92%",
//   },
//   {
//     invoiceNumber: "INV-003",
//     invoiceDate: "2025-10-20",
//     dueDate: "2025-11-20",
//     amountPayable: "2450",
//     currency: "EUR",
//     vendorName: "NextGen AI Labs",
//     customerName: "DataVerse Pvt Ltd",
//     ConfidenceScore: "92%",
//   },
//   {
//     invoiceNumber: "INV-003",
//     invoiceDate: "2025-10-20",
//     dueDate: "2025-11-20",
//     amountPayable: "2450",
//     currency: "EUR",
//     vendorName: "NextGen AI Labs",
//     customerName: "DataVerse Pvt Ltd",
//     ConfidenceScore: "92%",
//   },
//   {
//     invoiceNumber: "INV-003",
//     invoiceDate: "2025-10-20",
//     dueDate: "2025-11-20",
//     amountPayable: "2450",
//     currency: "EUR",
//     vendorName: "NextGen AI Labs",
//     customerName: "DataVerse Pvt Ltd",
//     ConfidenceScore: "92%",
//   },
//   {
//     invoiceNumber: "INV-003",
//     invoiceDate: "2025-10-20",
//     dueDate: "2025-11-20",
//     amountPayable: "2450",
//     currency: "EUR",
//     vendorName: "NextGen AI Labs",
//     customerName: "DataVerse Pvt Ltd",
//     ConfidenceScore: "92%",
//   },
//   {
//     invoiceNumber: "INV-003",
//     invoiceDate: "2025-10-20",
//     dueDate: "2025-11-20",
//     amountPayable: "2450",
//     currency: "EUR",
//     vendorName: "NextGen AI Labs",
//     customerName: "DataVerse Pvt Ltd",
//     ConfidenceScore: "92%",
//   },
//   {
//     invoiceNumber: "INV-003",
//     invoiceDate: "2025-10-20",
//     dueDate: "2025-11-20",
//     amountPayable: "2450",
//     currency: "EUR",
//     vendorName: "NextGen AI Labs",
//     customerName: "DataVerse Pvt Ltd",
//     ConfidenceScore: "92%",
//   },
// ];

export default function AnimatedListItemUse() {
  const { data: session } = useSession();
  const [items, setItems] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/api/v1/invoices/my_invoices",
          {
            headers: {
              Authorization: `Bearer ${session?.user?.token}`,
              "Content-Type": "application/json",
            },
          }
        );
        console.log(response.data);
        setItems(response.data);
      } catch (error) {
        console.error("Error fetching invoices:", error);
      } finally {
        setLoading(false);
      }
    };

    if (session?.user?.token) {
      fetchInvoices();
    }
  }, [session]);

  const handleVerify = async (index: number) => {
    if (!session?.user?.token) return;

    try {
      await axios.post(
        `http://localhost:8000/api/v1/invoices/my_invoices`,
        {},
        {
          headers: {
            Authorization: `Bearer ${session.user.token}`,
          },
        }
      );
      // Optionally refresh the list after verification
      // You could also just update the local state if the API returns the updated item
      console.log("Invoice verified:", items[index].invoiceNumber);
    } catch (error) {
      console.error("Error verifying invoice:", error);
    }
  };

  const itemsWithVerifyButton = items.map((item) => ({
    ...item,
    actions: (
      <Button
        onClick={(e) => {
          e.stopPropagation();
          const index = items.findIndex(
            (i) => i.invoiceNumber === item.invoiceNumber
          );
          handleVerify(index);
        }}
        variant="default"
        size="sm"
      >
        Verify
      </Button>
    ),
  }));

  if (loading) {
    return <div>Loading invoices...</div>;
  }

  return (
    <div className="w-full">
      <AnimatedList
        items={itemsWithVerifyButton}
        onItemSelect={(item, index) => console.log("Selected:", item, index)}
        showGradients={false}
        enableArrowNavigation={true}
        displayScrollbar={true}
      />
    </div>
  );
}

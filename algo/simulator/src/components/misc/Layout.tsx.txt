import React from "react";
import { PageHeader } from "./PageHeader";
import { Toaster } from "react-hot-toast";

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout = (props: LayoutProps) => {
  const { children } = props;

  return (
    <>
      <Toaster />
      <div className="p-4 min-h-[100vh] bg-gray-200 text-gray-900 flex flex-col">
        {/* Header */}
        <PageHeader />

        {/* Body */}
        <main className="flex-1">{children}</main>
      </div>
    </>
  );
};

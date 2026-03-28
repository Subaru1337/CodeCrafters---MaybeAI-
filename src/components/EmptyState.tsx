import React from "react";
import { LucideIcon, Inbox } from "lucide-react";

interface EmptyStateProps {
  message: string;
  icon?: LucideIcon;
  action?: { label: string; onClick: () => void };
}

const EmptyState = ({ message, icon: Icon = Inbox, action }: EmptyStateProps) => (
  <div className="flex flex-col items-center justify-center py-16 text-center">
    <div className="w-14 h-14 rounded-xl bg-muted flex items-center justify-center mb-4">
      <Icon className="w-7 h-7 text-muted-foreground" />
    </div>
    <p className="text-sm text-muted-foreground max-w-xs">{message}</p>
    {action && (
      <button
        onClick={action.onClick}
        className="mt-4 px-4 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition"
      >
        {action.label}
      </button>
    )}
  </div>
);

export default EmptyState;

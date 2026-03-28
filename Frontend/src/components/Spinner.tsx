import React from "react";

const Spinner = ({ message }: { message?: string }) => (
  <div className="flex flex-col items-center justify-center py-16">
    <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
    {message && <p className="mt-3 text-sm text-muted-foreground">{message}</p>}
  </div>
);

export default Spinner;

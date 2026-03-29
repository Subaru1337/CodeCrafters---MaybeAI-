import React, { useEffect, useState } from "react";
import { AlertTriangle, TrendingDown, Eye, Brain, Shield, Loader2, CheckCircle } from "lucide-react";
import client from "@/api/client";

type BiasResult = {
  user_id: number;
  is_biased: boolean;
  bias_warnings: string[];
  message?: string;
};

const iconMap: Record<string, React.ElementType> = {
  "Confirmation Bias": Eye,
  "FOMO": TrendingDown,
  "Diversification": Brain,
};

function getIcon(warning: string) {
  if (warning.includes("Confirmation")) return Eye;
  if (warning.includes("FOMO") || warning.includes("Herd")) return TrendingDown;
  return Brain;
}

function getSeverity(warning: string): "High" | "Medium" | "Low" {
  if (warning.startsWith("🚨")) return "High";
  if (warning.startsWith("⚠️")) return "Medium";
  return "Low";
}

const InsightsPage = () => {
  const [data, setData] = useState<BiasResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    client.get("/insights/biases")
      .then(res => setData(res.data))
      .catch(() => setError("Failed to load bias analysis. Make sure you have a portfolio built first."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Behavioural Insights</h1>
        <p className="text-sm text-muted-foreground mt-1">AI analysis of your portfolio allocation patterns</p>
      </div>

      {loading && (
        <div className="rounded-xl border border-border bg-card p-12 flex items-center justify-center gap-3">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
          <p className="text-sm text-muted-foreground">Analysing your portfolio…</p>
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-destructive mx-auto mb-2" />
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {data && !loading && (
        <>
          {/* Score banner */}
          <div className="rounded-xl border border-border bg-card p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Shield className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h2 className="font-semibold text-foreground">
                  {data.is_biased ? `${data.bias_warnings.length} Bias(es) Detected` : "No Biases Detected"}
                </h2>
                <p className="text-xs text-muted-foreground">Based on your latest saved portfolio</p>
              </div>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${data.is_biased ? "bg-warning" : "bg-success"}`}
                style={{ width: data.is_biased ? `${Math.min(data.bias_warnings.length * 33, 100)}%` : "10%" }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {data.is_biased ? "Review the warnings below to improve your allocation strategy." : "Your portfolio allocation looks well-balanced. Keep it up!"}
            </p>
          </div>

          {/* No biases state */}
          {!data.is_biased && (
            <div className="rounded-xl border border-success/30 bg-success/5 p-6 flex items-center gap-4">
              <CheckCircle className="w-8 h-8 text-success shrink-0" />
              <div>
                <p className="font-medium text-foreground">{data.message ?? "No behavioural biases detected in your current portfolio."}</p>
                <p className="text-sm text-muted-foreground mt-1">Build more portfolios and add more assets to get deeper insights over time.</p>
              </div>
            </div>
          )}

          {/* Individual bias cards */}
          {data.bias_warnings.length > 0 && (
            <div className="space-y-4">
              {data.bias_warnings.map((warning, i) => {
                const IconComp = getIcon(warning);
                const severity = getSeverity(warning);
                // Strip emoji prefix for display
                const clean = warning.replace(/^[🚨⚠️]\s*/, "");
                const [title, ...rest] = clean.split("]:");
                const titleClean = title.replace("[", "").trim();
                const description = rest.join("]:").trim();
                return (
                  <div key={i} className="rounded-xl border border-border bg-card p-5 space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${severity === "High" ? "bg-destructive/10" : severity === "Medium" ? "bg-warning/10" : "bg-muted"}`}>
                          <IconComp className={`w-5 h-5 ${severity === "High" ? "text-destructive" : severity === "Medium" ? "text-warning" : "text-muted-foreground"}`} />
                        </div>
                        <div>
                          <h3 className="font-semibold text-foreground">{titleClean}</h3>
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${severity === "High" ? "bg-destructive/10 text-destructive" : severity === "Medium" ? "bg-warning/10 text-warning" : "bg-muted text-muted-foreground"}`}>
                            {severity} Severity
                          </span>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-foreground/80">{description}</p>
                    <div className="rounded-lg bg-primary/5 border border-primary/10 p-3">
                      <p className="text-xs font-medium text-primary mb-1">Recommendation</p>
                      <p className="text-sm text-foreground/80">Review your allocation percentages and consider diversifying across more sectors and asset classes.</p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default InsightsPage;

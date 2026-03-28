import React from "react";
import { AlertTriangle, TrendingDown, Eye, Brain, Shield } from "lucide-react";

const mockBiases = [
  {
    name: "Recency Bias",
    severity: "High",
    description: "You've been overweighting stocks that performed well in the last 30 days, ignoring longer-term fundamentals.",
    recommendation: "Review 12-month performance data before making buy decisions. Your recent picks show 73% correlation with 30-day momentum.",
    icon: TrendingDown,
  },
  {
    name: "Confirmation Bias",
    severity: "Medium",
    description: "Your research queries predominantly search for bullish signals on stocks you already hold, potentially missing bearish indicators.",
    recommendation: "Try searching for bear cases on your top 3 holdings. Consider setting up alerts for negative sentiment changes.",
    icon: Eye,
  },
  {
    name: "Anchoring Bias",
    severity: "Low",
    description: "Your target prices appear anchored to purchase prices rather than fundamental valuations.",
    recommendation: "Re-evaluate exit prices based on current fundamentals rather than historical entry points.",
    icon: Brain,
  },
];

const InsightsPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Behavioural Insights</h1>
        <p className="text-sm text-muted-foreground mt-1">AI analysis of your investment patterns</p>
      </div>

      <div className="rounded-xl border border-border bg-card p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Shield className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h2 className="font-semibold text-foreground">Bias Score: 6.2/10</h2>
            <p className="text-xs text-muted-foreground">Based on your last 30 days of activity</p>
          </div>
        </div>
        <div className="h-2 rounded-full bg-muted overflow-hidden">
          <div className="h-full rounded-full bg-warning" style={{ width: "62%" }} />
        </div>
        <p className="text-xs text-muted-foreground mt-2">Lower is better. Average investor scores 7.5</p>
      </div>

      <div className="space-y-4">
        {mockBiases.map((bias) => (
          <div key={bias.name} className="rounded-xl border border-border bg-card p-5 space-y-3">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  bias.severity === "High" ? "bg-destructive/10" : bias.severity === "Medium" ? "bg-warning/10" : "bg-muted"
                }`}>
                  <bias.icon className={`w-5 h-5 ${
                    bias.severity === "High" ? "text-destructive" : bias.severity === "Medium" ? "text-warning" : "text-muted-foreground"
                  }`} />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">{bias.name}</h3>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    bias.severity === "High" ? "bg-destructive/10 text-destructive" : bias.severity === "Medium" ? "bg-warning/10 text-warning" : "bg-muted text-muted-foreground"
                  }`}>{bias.severity} Severity</span>
                </div>
              </div>
            </div>
            <p className="text-sm text-foreground/80">{bias.description}</p>
            <div className="rounded-lg bg-primary/5 border border-primary/10 p-3">
              <p className="text-xs font-medium text-primary mb-1">Recommendation</p>
              <p className="text-sm text-foreground/80">{bias.recommendation}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default InsightsPage;

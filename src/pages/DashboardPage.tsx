import React from "react";
import { useNavigate } from "react-router-dom";
import MetricCard from "@/components/MetricCard";
import {
  DollarSign,
  Shield,
  Target,
  Clock,
  PieChart,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle,
  Scale,
  Sparkles,
} from "lucide-react";
import { PieChart as RechartsPie, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Badge } from "@/components/ui/badge";

const mockPortfolio = [
  { name: "AAPL", value: 25, color: "hsl(145, 63%, 49%)" },
  { name: "GOOGL", value: 20, color: "hsl(200, 70%, 55%)" },
  { name: "MSFT", value: 18, color: "hsl(270, 60%, 60%)" },
  { name: "AMZN", value: 15, color: "hsl(38, 92%, 50%)" },
  { name: "TSLA", value: 12, color: "hsl(330, 65%, 55%)" },
  { name: "BONDS", value: 10, color: "hsl(220, 15%, 50%)" },
];

const mockWatchlist = [
  { name: "Reliance Industries", confidence: 0.85, sentiment: "Bullish" as const },
  { name: "TCS", confidence: 0.72, sentiment: "Neutral" as const },
  { name: "Infosys", confidence: 0.91, sentiment: "Bullish" as const },
  { name: "HDFC Bank", confidence: 0.44, sentiment: "Bearish" as const },
  { name: "Wipro", confidence: 0.68, sentiment: "Neutral" as const },
];

/** Demo alerts framed around Indian market compliance themes (SEBI-oriented copy; not legal advice). */
const complianceAlerts = [
  {
    id: "a1",
    severity: "warning" as const,
    title: "Concentration — single equity sleeve",
    body: "Technology US ADRs + India large-caps together exceed a diversified retail guideline. Consider documenting rationale or trimming to align with suitability.",
    ref: "SEBI / board suitability & concentration norms (illustrative)",
  },
  {
    id: "a2",
    severity: "info" as const,
    title: "Unlisted / illiquid exposure",
    body: "No unlisted names detected in this mock portfolio. If you add unlisted debt or equity, verify disclosure and valuation policy.",
    ref: "SEBI ICDR / AIF disclosures (when applicable)",
  },
];

const portfolioAiSuggestions = [
  {
    id: "s1",
    title: "Rebalance tech vs fixed income",
    detail: "Shift ~3% from top tech names into investment-grade bond funds to reduce drawdown risk with limited return impact (model estimate).",
  },
  {
    id: "s2",
    title: "Tax-aware harvesting",
    detail: "Before year-end, review STCG/LTCG on international holdings; pair with ELSS or loss harvesting only within policy (backend will compute).",
  },
];

const DashboardPage = () => {
  const navigate = useNavigate();
  const hasProfile = true;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Your financial intelligence overview</p>
      </div>

      {!hasProfile && (
        <div className="rounded-xl border border-primary/30 bg-primary/5 p-5 flex items-center justify-between">
          <div>
            <p className="font-semibold text-foreground">Complete your investor profile</p>
            <p className="text-sm text-muted-foreground mt-0.5">Get personalized recommendations</p>
          </div>
          <button type="button" onClick={() => navigate("/profile")} className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium">
            Set Up Profile
          </button>
        </div>
      )}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Capital" value="₹50L" subtitle="+12% YTD" icon={DollarSign} trend="up" />
        <MetricCard title="Risk Level" value="Moderate" subtitle="Level 3/5" icon={Shield} />
        <MetricCard title="Target Return" value="14%" subtitle="Annual goal" icon={Target} />
        <MetricCard title="Time Horizon" value="5 Years" subtitle="Long term" icon={Clock} />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="rounded-xl border border-border bg-card p-5 space-y-4">
          <div className="flex items-center justify-between mb-1">
            <h2 className="font-semibold text-foreground flex items-center gap-2">
              <PieChart className="w-4 h-4 text-primary" />
              Portfolio overview
            </h2>
            <button type="button" onClick={() => navigate("/portfolio")} className="text-xs text-primary font-medium hover:underline">
              View full →
            </button>
          </div>

          {complianceAlerts.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <Scale className="w-3.5 h-3.5" />
                Compliance &amp; policy alerts
              </div>
              {complianceAlerts.map((a) => (
                <div
                  key={a.id}
                  className={`rounded-lg border p-3 text-sm ${
                    a.severity === "warning"
                      ? "border-warning/40 bg-warning/5"
                      : "border-border bg-muted/30"
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <AlertTriangle className={`w-4 h-4 shrink-0 mt-0.5 ${a.severity === "warning" ? "text-warning" : "text-muted-foreground"}`} />
                    <div>
                      <p className="font-medium text-foreground">{a.title}</p>
                      <p className="text-muted-foreground mt-1 text-xs leading-relaxed">{a.body}</p>
                      <p className="text-[10px] text-muted-foreground mt-2 font-mono">{a.ref}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="rounded-lg border border-primary/20 bg-primary/5 p-3">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-xs font-semibold text-foreground">AI suggestions — optimize portfolio</span>
              <Badge variant="secondary" className="text-[10px]">
                Demo
              </Badge>
            </div>
            <ul className="space-y-2">
              {portfolioAiSuggestions.map((s) => (
                <li key={s.id} className="text-xs">
                  <span className="font-medium text-foreground">{s.title}: </span>
                  <span className="text-muted-foreground">{s.detail}</span>
                </li>
              ))}
            </ul>
            <button
              type="button"
              onClick={() => navigate("/portfolio")}
              className="mt-3 text-xs text-primary font-medium hover:underline"
            >
              Open portfolio AI chat to challenge these →
            </button>
          </div>

          <div className="flex items-center gap-6">
            <div className="w-32 h-32 shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPie>
                  <Pie data={mockPortfolio} dataKey="value" cx="50%" cy="50%" innerRadius={30} outerRadius={55} strokeWidth={2} stroke="hsl(var(--card))">
                    {mockPortfolio.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                </RechartsPie>
              </ResponsiveContainer>
            </div>
            <div className="space-y-2 flex-1 min-w-0">
              {mockPortfolio.slice(0, 3).map((item) => (
                <div key={item.name} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                    <span className="text-foreground font-medium truncate">{item.name}</span>
                  </div>
                  <span className="text-muted-foreground shrink-0">{item.value}%</span>
                </div>
              ))}
              <p className="text-xs text-muted-foreground">+{mockPortfolio.length - 3} more assets</p>
            </div>
          </div>
          <div className="pt-2 border-t border-border flex flex-wrap gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Expected return </span>
              <span className="text-success font-semibold">14.2%</span>
            </div>
            <div>
              <span className="text-muted-foreground">Sharpe </span>
              <span className="text-foreground font-semibold">1.4</span>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-foreground">Watchlist</h2>
            <button type="button" onClick={() => navigate("/research")} className="text-xs text-primary font-medium hover:underline">
              View all →
            </button>
          </div>
          <div className="space-y-3">
            {mockWatchlist.map((item) => (
              <div key={item.name} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                <span className="text-sm font-medium text-foreground">{item.name}</span>
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                      item.confidence > 0.7 ? "bg-success/10 text-success" : item.confidence > 0.4 ? "bg-warning/10 text-warning" : "bg-destructive/10 text-destructive"
                    }`}
                  >
                    {Math.round(item.confidence * 100)}%
                  </span>
                  <span
                    className={`flex items-center gap-0.5 text-xs font-medium ${
                      item.sentiment === "Bullish" ? "text-success" : item.sentiment === "Bearish" ? "text-destructive" : "text-muted-foreground"
                    }`}
                  >
                    {item.sentiment === "Bullish" ? <ArrowUpRight className="w-3 h-3" /> : null}
                    {item.sentiment === "Bearish" ? <ArrowDownRight className="w-3 h-3" /> : null}
                    {item.sentiment}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;

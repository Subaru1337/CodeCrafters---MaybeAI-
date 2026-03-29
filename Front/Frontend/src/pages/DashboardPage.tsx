import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MetricCard from "@/components/MetricCard";
import {
  DollarSign, Shield, Target, Clock, PieChart,
  ArrowUpRight, ArrowDownRight, Loader2, Sparkles,
} from "lucide-react";
import { PieChart as RechartsPie, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import client from "@/api/client";

const COLORS = [
  "hsl(145, 63%, 49%)", "hsl(200, 70%, 55%)", "hsl(270, 60%, 60%)",
  "hsl(38, 92%, 50%)", "hsl(330, 65%, 55%)", "hsl(220, 50%, 55%)",
  "hsl(15, 80%, 55%)", "hsl(180, 60%, 45%)",
];

const riskLabels = ["Very Conservative", "Conservative", "Moderate", "Aggressive", "Very Aggressive"];

const DashboardPage = () => {
  const navigate = useNavigate();

  const [profile, setProfile] = useState<any>(null);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      client.get("/profile"),
      client.get("/portfolio/latest"),
      client.get("/watchlist"),
    ]).then(([profileRes, portfolioRes, watchlistRes]) => {
      if (profileRes.status === "fulfilled") setProfile(profileRes.value.data);
      if (portfolioRes.status === "fulfilled") setPortfolio(portfolioRes.value.data);
      if (watchlistRes.status === "fulfilled") setWatchlist(watchlistRes.value.data);
    }).finally(() => setLoading(false));
  }, []);

  const formatCapital = (amount: number) => {
    if (!amount) return "—";
    if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
    return `₹${amount.toLocaleString()}`;
  };

  const pieData = portfolio
    ? Object.entries(portfolio.allocation as Record<string, number>).map(([name, value]) => ({ name, value: Math.round(value * 100) }))
    : [];

  if (loading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Your financial intelligence overview</p>
      </div>

      {!profile && (
        <div className="rounded-xl border border-primary/30 bg-primary/5 p-5 flex items-center justify-between">
          <div>
            <p className="font-semibold text-foreground">Complete your investor profile</p>
            <p className="text-sm text-muted-foreground mt-0.5">Get personalized recommendations</p>
          </div>
          <button type="button" onClick={() => navigate("/profile")}
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium">
            Set Up Profile
          </button>
        </div>
      )}

      {/* Metric cards from real profile */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Capital"
          value={profile ? formatCapital(profile.capital_amount) : "—"}
          subtitle={profile ? `${profile.preferred_language ?? "English"}` : "No profile"}
          icon={DollarSign}
          trend="up"
        />
        <MetricCard
          title="Risk Level"
          value={profile ? riskLabels[(profile.risk_level ?? 3) - 1] : "—"}
          subtitle={profile ? `Level ${profile.risk_level}/5` : "No profile"}
          icon={Shield}
        />
        <MetricCard
          title="Target Return"
          value={profile ? `${profile.target_return_pct ?? "—"}%` : "—"}
          subtitle="Annual goal"
          icon={Target}
        />
        <MetricCard
          title="Time Horizon"
          value={profile ? `${profile.time_horizon_years} Years` : "—"}
          subtitle={profile ? (profile.time_horizon_years >= 10 ? "Long term" : "Medium term") : "No profile"}
          icon={Clock}
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Portfolio overview */}
        <div className="rounded-xl border border-border bg-card p-5 space-y-4">
          <div className="flex items-center justify-between mb-1">
            <h2 className="font-semibold text-foreground flex items-center gap-2">
              <PieChart className="w-4 h-4 text-primary" />
              Portfolio overview
            </h2>
            <button type="button" onClick={() => navigate("/portfolio")}
              className="text-xs text-primary font-medium hover:underline">
              View full →
            </button>
          </div>

          {!portfolio ? (
            <div className="text-center py-6">
              <p className="text-sm text-muted-foreground mb-3">No portfolio yet.</p>
              <button type="button" onClick={() => navigate("/portfolio")}
                className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium">
                Build Portfolio
              </button>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-6">
                <div className="w-32 h-32 shrink-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPie>
                      <Pie data={pieData} dataKey="value" cx="50%" cy="50%" innerRadius={30} outerRadius={55} strokeWidth={2} stroke="hsl(var(--card))">
                        {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }} />
                    </RechartsPie>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-2 flex-1 min-w-0">
                  {pieData.slice(0, 4).map((item, i) => (
                    <div key={item.name} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2 min-w-0">
                        <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                        <span className="text-foreground font-medium truncate">{item.name}</span>
                      </div>
                      <span className="text-muted-foreground shrink-0">{item.value}%</span>
                    </div>
                  ))}
                  {pieData.length > 4 && <p className="text-xs text-muted-foreground">+{pieData.length - 4} more</p>}
                </div>
              </div>
              <div className="pt-2 border-t border-border flex flex-wrap gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Expected return </span>
                  <span className="text-success font-semibold">{(portfolio.expected_return * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Sharpe </span>
                  <span className="text-foreground font-semibold">{portfolio.sharpe_ratio.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Volatility </span>
                  <span className="text-warning font-semibold">{(portfolio.expected_volatility * 100).toFixed(1)}%</span>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Live Watchlist */}
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-foreground">Watchlist</h2>
            <button type="button" onClick={() => navigate("/research")}
              className="text-xs text-primary font-medium hover:underline">
              View all →
            </button>
          </div>
          <div className="space-y-3">
            {watchlist.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                No watchlist items. <button onClick={() => navigate("/research")} className="text-primary underline">Add companies</button>
              </p>
            ) : (
              watchlist.map((item) => (
                <div key={item.id} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <span className="text-sm font-medium text-foreground">Company #{item.company_id}</span>
                  <span className="text-xs text-muted-foreground">Added {new Date(item.added_at).toLocaleDateString()}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Reasoning from last portfolio */}
      {portfolio?.reasoning && (
        <div className="rounded-xl border border-primary/20 bg-primary/5 p-5">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm font-semibold text-foreground">AI Portfolio Reasoning</span>
          </div>
          <p className="text-sm text-foreground/80 leading-relaxed">{portfolio.reasoning}</p>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;

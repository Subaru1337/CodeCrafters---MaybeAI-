import React, { useEffect, useState } from "react";
import { PieChart as RechartsPie, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { RefreshCw, History, TrendingUp, Activity, BarChart3, Loader2, MessageSquare, Zap, ArrowRight, ArrowUp, ArrowDown } from "lucide-react";
import Spinner from "@/components/Spinner";
import { PortfolioFinanceChat } from "@/components/portfolio/PortfolioFinanceChat";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import client from "@/api/client";

const COLORS = [
  "hsl(145, 63%, 49%)", "hsl(200, 70%, 55%)", "hsl(270, 60%, 60%)",
  "hsl(38, 92%, 50%)", "hsl(330, 65%, 55%)", "hsl(220, 50%, 55%)",
  "hsl(15, 80%, 55%)", "hsl(180, 60%, 45%)",
];

type Portfolio = {
  id: number;
  user_id: number;
  allocation: Record<string, number>;
  expected_return: number;
  expected_volatility: number;
  sharpe_ratio: number;
  reasoning: string | null;
  created_at: string;
};

type SimResult = {
  new_allocation: Record<string, number>;
  new_expected_return: number;
  new_expected_volatility: number;
  new_sharpe_ratio: number;
  delta_return: number | null;
  delta_volatility: number | null;
};

// ── Helper: render a mini donut ──────────────────────────────
function MiniPie({ data }: { data: { name: string; value: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={180}>
      <RechartsPie>
        <Pie data={data} dataKey="value" cx="50%" cy="50%" innerRadius={40} outerRadius={70}
          strokeWidth={2} stroke="hsl(var(--card))"
          label={({ name, value }) => `${name} ${value.toFixed(1)}%`}
          labelLine={false}>
          {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Pie>
        <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px", fontSize: "11px" }}
          formatter={(v: any) => `${Number(v).toFixed(1)}%`} />
      </RechartsPie>
    </ResponsiveContainer>
  );
}

// ── Delta badge ──────────────────────────────────────────────
function Delta({ label, current, simulated, unit = "%" }: { label: string; current: number; simulated: number; unit?: string }) {
  const diff = simulated - current;
  const positive = diff > 0;
  const color = label.includes("Volatility") ? (positive ? "text-destructive" : "text-success") : (positive ? "text-success" : "text-destructive");
  return (
    <div className="flex flex-col items-center gap-0.5">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-semibold text-foreground">{(simulated * 100).toFixed(1)}{unit}</p>
      <p className={`text-xs flex items-center gap-0.5 font-medium ${color}`}>
        {positive ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
        {Math.abs(diff * 100).toFixed(1)}{unit}
      </p>
    </div>
  );
}

const PortfolioPage = () => {
  const { toast } = useToast();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [history, setHistory] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [building, setBuilding] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [pendingChatMessage, setPendingChatMessage] = useState<string | null>(null);
  const [pendingMessageToken, setPendingMessageToken] = useState<string | null>(null);

  // What-If state
  const [showWhatIf, setShowWhatIf] = useState(false);
  const [simRisk, setSimRisk] = useState<number>(3);
  const [simCapital, setSimCapital] = useState<string>("");
  const [simulating, setSimulating] = useState(false);
  const [simResult, setSimResult] = useState<SimResult | null>(null);

  useEffect(() => {
    client.get("/portfolio/latest")
      .then(res => {
        setPortfolio(res.data);
        setSimRisk(3); // default
      })
      .catch(() => setPortfolio(null))
      .finally(() => setLoading(false));
  }, []);

  const loadHistory = async () => {
    if (!showHistory) {
      const res = await client.get("/portfolio/history").catch(() => ({ data: [] }));
      setHistory(res.data);
    }
    setShowHistory(prev => !prev);
  };

  const handleBuild = async () => {
    setBuilding(true);
    try {
      const res = await client.post("/portfolio/build");
      setPortfolio(res.data);
      setSimResult(null);
      toast({ title: "Portfolio built successfully! ✅" });
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? "Failed to build portfolio.";
      toast({ title: msg, variant: "destructive" });
    } finally {
      setBuilding(false);
    }
  };

  const handleSimulate = async () => {
    setSimulating(true);
    setSimResult(null);
    try {
      const body: Record<string, any> = { risk_level_override: simRisk };
      if (simCapital && Number(simCapital) > 0) body.capital_override = Number(simCapital);
      const res = await client.post("/portfolio/simulate", body);
      setSimResult(res.data);
    } catch (err: any) {
      toast({ title: err?.response?.data?.detail ?? "Simulation failed.", variant: "destructive" });
    } finally {
      setSimulating(false);
    }
  };

  const pieData = portfolio
    ? Object.entries(portfolio.allocation).map(([name, value]) => ({
        name,
        value: Math.round(value * 10) / 10,
      }))
    : [];

  const simPieData = simResult
    ? Object.entries(simResult.new_allocation).map(([name, value]) => ({
        name,
        value: Math.round(value * 10) / 10,
      }))
    : [];

  const portfolioSummary = portfolio
    ? `Return: ${(portfolio.expected_return * 100).toFixed(1)}%, Volatility: ${(portfolio.expected_volatility * 100).toFixed(1)}%, Sharpe: ${portfolio.sharpe_ratio.toFixed(2)}`
    : "";

  if (loading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  if (building) return <Spinner message="Optimizing your portfolio with cvxpy..." />;

  return (
    <div className="space-y-6 pb-24">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Portfolio</h1>
          <p className="text-sm text-muted-foreground mt-1">AI-optimized asset allocation via Convex Optimizer</p>
        </div>
        <div className="flex gap-2">
          {portfolio && (
            <>
              <button type="button" onClick={loadHistory}
                className="px-3 py-2 rounded-lg border border-border text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition flex items-center gap-1.5">
                <History className="w-4 h-4" /> History
              </button>
              <button type="button" onClick={() => { setShowWhatIf(p => !p); setSimResult(null); }}
                className={`px-3 py-2 rounded-lg border text-sm font-medium transition flex items-center gap-1.5 ${showWhatIf ? "bg-primary/10 border-primary text-primary" : "border-border text-muted-foreground hover:text-foreground hover:bg-accent"}`}>
                <Zap className="w-4 h-4" /> What-If
              </button>
            </>
          )}
          <button type="button" onClick={handleBuild}
            className="px-3 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition flex items-center gap-1.5">
            <RefreshCw className="w-4 h-4" /> {portfolio ? "Rebuild" : "Build Portfolio"}
          </button>
        </div>
      </div>

      {!portfolio ? (
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-foreground mb-2">No Portfolio Yet</h2>
          <p className="text-sm text-muted-foreground mb-6">Build a portfolio optimized for your investor profile using our AI Convex Optimizer.</p>
          <button type="button" onClick={handleBuild}
            className="px-6 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition">
            Build My Portfolio
          </button>
        </div>
      ) : (
        <>
          {/* Key metrics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="rounded-xl border border-border bg-card p-5 text-center">
              <TrendingUp className="w-5 h-5 text-success mx-auto mb-2" />
              <p className="text-2xl font-bold text-success">{(portfolio.expected_return * 100).toFixed(1)}%</p>
              <p className="text-xs text-muted-foreground mt-1">Expected Annual Return</p>
            </div>
            <div className="rounded-xl border border-border bg-card p-5 text-center">
              <Activity className="w-5 h-5 text-warning mx-auto mb-2" />
              <p className="text-2xl font-bold text-foreground">{(portfolio.expected_volatility * 100).toFixed(1)}%</p>
              <p className="text-xs text-muted-foreground mt-1">Portfolio Volatility</p>
            </div>
            <div className="rounded-xl border border-border bg-card p-5 text-center">
              <BarChart3 className="w-5 h-5 text-primary mx-auto mb-2" />
              <p className="text-2xl font-bold text-foreground">{portfolio.sharpe_ratio.toFixed(2)}</p>
              <p className="text-xs text-muted-foreground mt-1">Sharpe Ratio</p>
            </div>
          </div>

          {/* ── What-If Scenario Engine ─────────────────────────────── */}
          {showWhatIf && (
            <div className="rounded-xl border border-primary/30 bg-primary/5 p-5 space-y-5">
              <div className="flex items-center gap-2 mb-1">
                <Zap className="w-4 h-4 text-primary" />
                <h3 className="font-semibold text-foreground">What-If Scenario Engine</h3>
                <span className="text-xs text-muted-foreground ml-auto">Adjust parameters and simulate a new portfolio</span>
              </div>

              {/* Controls */}
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Risk Level Override: <span className="text-primary font-bold">{simRisk}</span>
                    <span className="ml-1 text-muted-foreground normal-case font-normal">
                      ({["", "Very Conservative", "Conservative", "Moderate", "Aggressive", "Very Aggressive"][simRisk]})
                    </span>
                  </label>
                  <input type="range" min={1} max={5} step={1} value={simRisk}
                    onChange={e => { setSimRisk(Number(e.target.value)); setSimResult(null); }}
                    className="w-full mt-2 accent-primary" />
                  <div className="flex justify-between text-xs text-muted-foreground mt-0.5">
                    <span>1</span><span>2</span><span>3</span><span>4</span><span>5</span>
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Capital Override <span className="normal-case font-normal">(optional)</span>
                  </label>
                  <input type="number" value={simCapital} placeholder="Leave blank to keep current"
                    onChange={e => { setSimCapital(e.target.value); setSimResult(null); }}
                    className="w-full mt-2 rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50" />
                </div>
              </div>

              <Button type="button" onClick={handleSimulate} disabled={simulating}
                className="flex items-center gap-2">
                {simulating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                {simulating ? "Simulating…" : "Run Simulation"}
              </Button>

              {/* Side-by-side comparison */}
              {simResult && (
                <div className="space-y-4 pt-2 border-t border-border/50">
                  <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-primary" />
                    Comparison: Current vs Simulated (Risk {simRisk})
                  </h4>

                  {/* Delta metrics bar */}
                  <div className="grid grid-cols-3 gap-3 rounded-lg bg-background border border-border p-4 text-center">
                    <Delta label="Expected Return" current={portfolio.expected_return} simulated={simResult.new_expected_return} />
                    <Delta label="Volatility" current={portfolio.expected_volatility} simulated={simResult.new_expected_volatility} />
                    <div className="flex flex-col items-center gap-0.5">
                      <p className="text-xs text-muted-foreground">Sharpe Ratio</p>
                      <p className="font-semibold text-foreground">{simResult.new_sharpe_ratio.toFixed(2)}</p>
                      <p className={`text-xs flex items-center gap-0.5 font-medium ${simResult.new_sharpe_ratio > portfolio.sharpe_ratio ? "text-success" : "text-destructive"}`}>
                        {simResult.new_sharpe_ratio > portfolio.sharpe_ratio ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                        {Math.abs(simResult.new_sharpe_ratio - portfolio.sharpe_ratio).toFixed(2)}
                      </p>
                    </div>
                  </div>

                  {/* Two pie charts */}
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div className="rounded-lg border border-border bg-card p-4">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 text-center">Current Portfolio</p>
                      <MiniPie data={pieData} />
                    </div>
                    <div className="rounded-lg border border-primary/30 bg-primary/5 p-4">
                      <p className="text-xs font-semibold text-primary uppercase tracking-wide mb-2 text-center">Simulated (Risk {simRisk})</p>
                      <MiniPie data={simPieData} />
                    </div>
                  </div>

                  {/* Simulated breakdown table */}
                  <div className="rounded-lg border border-border bg-card p-4">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">Simulated Allocation Breakdown</p>
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="text-left py-1.5 text-muted-foreground font-medium">Ticker</th>
                          <th className="text-right py-1.5 text-muted-foreground font-medium">Current</th>
                          <th className="text-right py-1.5 text-muted-foreground font-medium">Simulated</th>
                          <th className="text-right py-1.5 text-muted-foreground font-medium">Δ</th>
                        </tr>
                      </thead>
                      <tbody>
                        {simPieData.sort((a, b) => b.value - a.value).map((d, i) => {
                          const currentVal = portfolio.allocation[d.name] ?? 0;
                          const diff = d.value - Math.round(currentVal * 10) / 10;
                          return (
                            <tr key={d.name} className="border-b border-border/40 last:border-0">
                              <td className="py-2 font-medium text-foreground flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                                {d.name}
                              </td>
                              <td className="text-right py-2 text-muted-foreground">{Math.round(currentVal * 10) / 10}%</td>
                              <td className="text-right py-2 text-foreground font-medium">{d.value.toFixed(1)}%</td>
                              <td className={`text-right py-2 text-xs font-medium ${diff > 0.05 ? "text-success" : diff < -0.05 ? "text-destructive" : "text-muted-foreground"}`}>
                                {diff > 0.05 ? "+" : ""}{diff.toFixed(1)}%
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Charts */}
          <div className="grid lg:grid-cols-2 gap-6">
            <div className="rounded-xl border border-border bg-card p-6">
              <h3 className="font-semibold text-foreground mb-4">Allocation</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPie>
                    <Pie data={pieData} dataKey="value" cx="50%" cy="50%" innerRadius={50} outerRadius={90}
                      strokeWidth={2} stroke="hsl(var(--card))"
                      label={({ name, value }) => `${name} ${value.toFixed(1)}%`}>
                      {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }}
                      formatter={(v: any) => `${Number(v).toFixed(1)}%`} />
                  </RechartsPie>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card p-6">
              <h3 className="font-semibold text-foreground mb-4">Breakdown</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 text-muted-foreground font-medium">Ticker</th>
                      <th className="text-right py-2 text-muted-foreground font-medium">Allocation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pieData.sort((a, b) => b.value - a.value).map((d, i) => (
                      <tr key={d.name} className="border-b border-border/50 last:border-0">
                        <td className="py-2.5 font-medium text-foreground flex items-center gap-2">
                          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                          {d.name}
                        </td>
                        <td className="text-right py-2.5 text-foreground">{d.value.toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="text-xs text-muted-foreground mt-3">
                Built on {new Date(portfolio.created_at).toLocaleDateString(undefined, { dateStyle: "medium" })}
              </p>
            </div>
          </div>

          {/* AI Reasoning */}
          {portfolio.reasoning && (
            <div className="rounded-xl border border-primary/20 bg-primary/5 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-foreground mb-1 flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-primary" />
                    AI reasoning
                  </h3>
                  <p className="text-sm text-foreground/80 leading-relaxed">{portfolio.reasoning}</p>
                </div>
                <Button type="button" variant="secondary" size="sm" className="shrink-0"
                  onClick={() => {
                    setPendingChatMessage("Explain the main drivers of this allocation and key risks.");
                    setPendingMessageToken(crypto.randomUUID ? crypto.randomUUID() : `t-${Date.now()}`);
                    setChatOpen(true);
                  }}>
                  Open in chat
                </Button>
              </div>
            </div>
          )}

          {/* History */}
          {showHistory && (
            <div className="rounded-xl border border-border bg-card p-5 animate-fade-in">
              <h3 className="font-semibold text-foreground mb-3">Portfolio History</h3>
              <div className="space-y-2">
                {history.map((h) => (
                  <div key={h.id} className={`flex items-center justify-between py-2 px-3 rounded-lg ${h.id === portfolio.id ? "bg-primary/10" : ""}`}>
                    <span className="text-sm text-foreground">{new Date(h.created_at).toLocaleDateString(undefined, { dateStyle: "medium" })}</span>
                    <span className="text-sm text-success font-medium">{(h.expected_return * 100).toFixed(1)}% return</span>
                    {h.id === portfolio.id && <span className="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded-full">Current</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {portfolio && (
        <PortfolioFinanceChat
          open={chatOpen}
          onOpenChange={setChatOpen}
          portfolioSummary={portfolioSummary}
          initialUserMessage={pendingChatMessage}
          initialMessageToken={pendingMessageToken}
          onConsumeInitialMessage={() => { setPendingChatMessage(null); setPendingMessageToken(null); }}
        />
      )}
    </div>
  );
};

export default PortfolioPage;

import React, { useMemo, useState } from "react";
import { PieChart as RechartsPie, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { RefreshCw, Share2, History, TrendingUp, Activity, BarChart3, Lightbulb, MessageSquare } from "lucide-react";
import Spinner from "@/components/Spinner";
import { PortfolioFinanceChat } from "@/components/portfolio/PortfolioFinanceChat";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const COLORS = [
  "hsl(145, 63%, 49%)",
  "hsl(200, 70%, 55%)",
  "hsl(270, 60%, 60%)",
  "hsl(38, 92%, 50%)",
  "hsl(330, 65%, 55%)",
  "hsl(220, 50%, 55%)",
  "hsl(15, 80%, 55%)",
  "hsl(180, 60%, 45%)",
];

const mockPortfolioData = [
  { ticker: "AAPL", allocation: 22, contribution: 3.1 },
  { ticker: "GOOGL", allocation: 18, contribution: 2.5 },
  { ticker: "MSFT", allocation: 16, contribution: 2.3 },
  { ticker: "RELIANCE", allocation: 14, contribution: 2.0 },
  { ticker: "TCS", allocation: 10, contribution: 1.4 },
  { ticker: "BONDS", allocation: 10, contribution: 0.8 },
  { ticker: "GOLD", allocation: 6, contribution: 0.7 },
  { ticker: "CASH", allocation: 4, contribution: 0.4 },
];

const aiRecommendations = [
  {
    id: "r1",
    title: "Reduce single-name tech concentration",
    detail:
      "Combined AAPL + GOOGL + MSFT is 56%. SEBI-style diversification checks often flag issuer concentration above ~40–50% in similar sleeves for retail portfolios.",
    action: "Trim 4–6% from the top two names and add to BONDS or a broad index.",
  },
  {
    id: "r2",
    title: "Lift fixed income to match moderate risk",
    detail: "At 10% bonds + 4% cash, the portfolio is growth-heavy. A modest shift can lower drawdowns without sacrificing much expected return.",
    action: "Consider +3–5% to high-quality bond / gilt funds.",
  },
  {
    id: "r3",
    title: "Rebalance domestic vs global",
    detail: "India allocations (Reliance, TCS) pair well with global tech but watch currency and sector overlap.",
    action: "Review quarterly so one sleeve does not drift past policy limits.",
  },
];

const reasoningSummary =
  "Optimized for moderate risk, ₹50L capital, 5-year horizon: growth via global tech and India large-caps, ballast via bonds and gold, small cash buffer for rebalancing.";

const PortfolioPage = () => {
  const [hasPortfolio, setHasPortfolio] = useState(true);
  const [building, setBuilding] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [pendingChatMessage, setPendingChatMessage] = useState<string | null>(null);
  const [pendingMessageToken, setPendingMessageToken] = useState<string | null>(null);

  const pieData = mockPortfolioData.map((d) => ({ name: d.ticker, value: d.allocation }));

  const portfolioSummary = useMemo(() => {
    const tech = mockPortfolioData.filter((d) => ["AAPL", "GOOGL", "MSFT"].includes(d.ticker)).reduce((s, d) => s + d.allocation, 0);
    return `${tech}% tech, ${mockPortfolioData.find((d) => d.ticker === "BONDS")?.allocation ?? 0}% bonds, gold and India large-caps for balance`;
  }, []);

  const handleBuild = () => {
    setBuilding(true);
    setTimeout(() => {
      setBuilding(false);
      setHasPortfolio(true);
    }, 2500);
  };

  const challengeRecommendation = (title: string) => {
    setPendingChatMessage(`Challenge this recommendation: "${title}". Why was it chosen for my portfolio?`);
    setPendingMessageToken(typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `t-${Date.now()}`);
    setChatOpen(true);
  };

  if (building) return <Spinner message="Optimizing your portfolio..." />;

  return (
    <div className="space-y-6 pb-24">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Portfolio</h1>
          <p className="text-sm text-muted-foreground mt-1">AI-optimized asset allocation</p>
        </div>
        {hasPortfolio && (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setShowHistory(!showHistory)}
              className="px-3 py-2 rounded-lg border border-border text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition flex items-center gap-1.5"
            >
              <History className="w-4 h-4" /> History
            </button>
            <button
              type="button"
              className="px-3 py-2 rounded-lg border border-border text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition flex items-center gap-1.5"
            >
              <Share2 className="w-4 h-4" /> Share
            </button>
            <button
              type="button"
              onClick={handleBuild}
              className="px-3 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition flex items-center gap-1.5"
            >
              <RefreshCw className="w-4 h-4" /> Rebuild
            </button>
          </div>
        )}
      </div>

      {!hasPortfolio ? (
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-foreground mb-2">No Portfolio Yet</h2>
          <p className="text-sm text-muted-foreground mb-6">Build a portfolio optimized for your investor profile</p>
          <button type="button" onClick={handleBuild} className="px-6 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition">
            Build My Portfolio
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-4">
            <div className="rounded-xl border border-border bg-card p-5 text-center">
              <TrendingUp className="w-5 h-5 text-success mx-auto mb-2" />
              <p className="text-2xl font-bold text-success">14.2%</p>
              <p className="text-xs text-muted-foreground mt-1">Expected Annual Return</p>
            </div>
            <div className="rounded-xl border border-border bg-card p-5 text-center">
              <Activity className="w-5 h-5 text-warning mx-auto mb-2" />
              <p className="text-2xl font-bold text-foreground">8.3%</p>
              <p className="text-xs text-muted-foreground mt-1">Portfolio Volatility</p>
            </div>
            <div className="rounded-xl border border-border bg-card p-5 text-center">
              <BarChart3 className="w-5 h-5 text-primary mx-auto mb-2" />
              <p className="text-2xl font-bold text-foreground">1.4</p>
              <p className="text-xs text-muted-foreground mt-1">Sharpe Ratio</p>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            <div className="rounded-xl border border-border bg-card p-6">
              <h3 className="font-semibold text-foreground mb-4">Allocation</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPie>
                    <Pie
                      data={pieData}
                      dataKey="value"
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={90}
                      strokeWidth={2}
                      stroke="hsl(var(--card))"
                      label={({ name, value }) => `${name} ${value}%`}
                    >
                      {pieData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
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
            </div>

            <div className="rounded-xl border border-border bg-card p-6">
              <h3 className="font-semibold text-foreground mb-4">Breakdown</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 text-muted-foreground font-medium">Ticker</th>
                      <th className="text-right py-2 text-muted-foreground font-medium">Allocation</th>
                      <th className="text-right py-2 text-muted-foreground font-medium">Contribution</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockPortfolioData.map((d, i) => (
                      <tr key={d.ticker} className="border-b border-border/50 last:border-0">
                        <td className="py-2.5 font-medium text-foreground flex items-center gap-2">
                          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                          {d.ticker}
                        </td>
                        <td className="text-right py-2.5 text-foreground">{d.allocation}%</td>
                        <td className="text-right py-2.5 text-success">+{d.contribution}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-primary/20 bg-primary/5 p-5">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
              <div>
                <h3 className="font-semibold text-foreground mb-1 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-primary" />
                  AI reasoning (summary)
                </h3>
                <p className="text-sm text-foreground/80 leading-relaxed">{reasoningSummary}</p>
              </div>
              <Button
                type="button"
                variant="secondary"
                size="sm"
                className="shrink-0"
                onClick={() => {
                  setPendingChatMessage("Explain the main drivers of this allocation and key risks.");
                  setPendingMessageToken(typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `t-${Date.now()}`);
                  setChatOpen(true);
                }}
              >
                Open in chat
              </Button>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-5 h-5 text-primary" />
              <h3 className="text-lg font-semibold text-foreground">AI recommendations</h3>
              <Badge variant="secondary" className="text-xs">
                Portfolio-based
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              Suggestions grounded in your current mix. Use the chat to challenge any line item and ask for justification.
            </p>
            <div className="grid md:grid-cols-1 gap-4">
              {aiRecommendations.map((r) => (
                <Card key={r.id}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">{r.title}</CardTitle>
                    <CardDescription className="text-sm leading-relaxed">{r.detail}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-sm">
                      <span className="font-medium text-foreground">Suggested action: </span>
                      {r.action}
                    </p>
                    <Button type="button" variant="outline" size="sm" onClick={() => challengeRecommendation(r.title)}>
                      Challenge in AI chat
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {showHistory && (
            <div className="rounded-xl border border-border bg-card p-5 animate-fade-in">
              <h3 className="font-semibold text-foreground mb-3">Portfolio History</h3>
              <div className="space-y-2">
                {[
                  { date: "Mar 28, 2026", ret: "14.2%", current: true },
                  { date: "Mar 15, 2026", ret: "13.8%", current: false },
                  { date: "Feb 28, 2026", ret: "12.1%", current: false },
                ].map((h) => (
                  <div key={h.date} className={`flex items-center justify-between py-2 px-3 rounded-lg ${h.current ? "bg-primary/10" : ""}`}>
                    <span className="text-sm text-foreground">{h.date}</span>
                    <span className="text-sm text-success font-medium">{h.ret}</span>
                    {h.current && (
                      <span className="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded-full">Current</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {hasPortfolio && (
        <PortfolioFinanceChat
          open={chatOpen}
          onOpenChange={setChatOpen}
          portfolioSummary={portfolioSummary}
          initialUserMessage={pendingChatMessage}
          initialMessageToken={pendingMessageToken}
          onConsumeInitialMessage={() => {
            setPendingChatMessage(null);
            setPendingMessageToken(null);
          }}
        />
      )}
    </div>
  );
};

export default PortfolioPage;

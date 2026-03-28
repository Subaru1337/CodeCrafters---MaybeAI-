import React, { useMemo, useState } from "react";
import { Search, ArrowUpRight, ArrowDownRight, AlertTriangle, CheckCircle, Plus, X, Star, Newspaper, BookOpen } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type EntityType = "stock" | "fund" | "term";

type ResearchEntity = {
  key: string;
  type: EntityType;
  name: string;
  ticker?: string;
  summary: string;
  confidence: number;
  sentiment: string;
  sentiment_score: number;
  conflict: string | null;
  sources: string[];
  extra?: string;
};

const mockResults: Record<string, ResearchEntity> = {
  reliance: {
    key: "reliance",
    type: "stock",
    name: "Reliance Industries",
    ticker: "RELIANCE.NS",
    summary:
      "Reliance Industries continues to show strong momentum driven by its digital and retail segments. Jio Platforms reported 18% YoY revenue growth, while retail expansion added 2,500 new stores this quarter.",
    confidence: 0.85,
    sentiment: "Bullish",
    sentiment_score: 0.78,
    conflict: null,
    sources: ["Bloomberg", "Reuters", "SEBI Filings", "Economic Times"],
  },
  tcs: {
    key: "tcs",
    type: "stock",
    name: "Tata Consultancy Services",
    ticker: "TCS.NS",
    summary:
      "TCS delivered steady Q3 results with 3.2% QoQ revenue growth in constant currency. Deal wins remained robust at $8.1B TCV. Attrition has ticked up and BFSI shows some slowdown.",
    confidence: 0.72,
    sentiment: "Neutral",
    sentiment_score: 0.52,
    conflict:
      "Goldman Sachs rates TCS as 'Sell' citing margin pressure, while Morgan Stanley maintains 'Overweight' based on deal pipeline strength.",
    sources: ["Goldman Sachs Research", "Morgan Stanley", "NSE Filings"],
  },
  infosys: {
    key: "infosys",
    type: "stock",
    name: "Infosys Limited",
    ticker: "INFY.NS",
    summary:
      "Infosys raised revenue growth guidance after strong large deal wins. Generative AI engagements are accelerating. Operating margins improved sequentially.",
    confidence: 0.91,
    sentiment: "Bullish",
    sentiment_score: 0.83,
    conflict: null,
    sources: ["Company Filings", "CNBC", "Motilal Oswal Research", "Bloomberg"],
  },
  "hdfc flexi cap": {
    key: "hdfc flexi cap",
    type: "fund",
    name: "HDFC Flexi Cap Fund",
    ticker: "INF174K01LS2",
    summary:
      "A large flexi-cap fund with flexibility across market caps. Historically overweight quality and domestic cyclicals; expense ratio competitive in category. Suitability: long-term wealth, moderate–high risk tolerance.",
    confidence: 0.88,
    sentiment: "Neutral",
    sentiment_score: 0.62,
    conflict: null,
    sources: ["AMFI", "Scheme document", "Morningstar"],
    extra: "Category: Flexi Cap · Benchmark: NIFTY 500 TRI (illustrative)",
  },
  "nippon india etf": {
    key: "nippon india etf",
    type: "fund",
    name: "Nippon India ETF Nifty BeES",
    ticker: "NIFTYBEES",
    summary:
      "Among the most liquid Nifty 50 ETFs in India. Tight tracking error vs index; use for core equity exposure with low active risk.",
    confidence: 0.9,
    sentiment: "Neutral",
    sentiment_score: 0.55,
    conflict: null,
    sources: ["NSE", "AMFI"],
    extra: "Type: ETF · Expense ratio typically low vs active funds",
  },
  sip: {
    key: "sip",
    type: "term",
    name: "SIP (Systematic Investment Plan)",
    summary:
      "A disciplined way to invest a fixed sum regularly in mutual funds. Averages purchase cost over time (rupee cost averaging) and suits salaried investors building long-term goals.",
    confidence: 0.95,
    sentiment: "Neutral",
    sentiment_score: 0.5,
    conflict: null,
    sources: ["SEBI investor guides", "AMFI"],
    extra: "Not a product—it's a mode of investing into a scheme.",
  },
  elss: {
    key: "elss",
    type: "term",
    name: "ELSS (Equity Linked Savings Scheme)",
    summary:
      "Tax-saving mutual fund category under Section 80C with a three-year lock-in. Predominantly equity-oriented; returns are market-linked.",
    confidence: 0.92,
    sentiment: "Neutral",
    sentiment_score: 0.48,
    conflict: null,
    sources: ["Income Tax Act references", "AMFI"],
    extra: "Lock-in: 3 years · 80C limit shared with other instruments",
  },
  sharpe: {
    key: "sharpe",
    type: "term",
    name: "Sharpe ratio",
    summary:
      "Risk-adjusted return measure: excess return per unit of volatility. Higher is generally better when comparing similar strategies. Not a prediction of future performance.",
    confidence: 0.9,
    sentiment: "Neutral",
    sentiment_score: 0.5,
    conflict: null,
    sources: ["CFA Institute", "Academic literature"],
  },
};

const latestNews = [
  {
    id: "n1",
    title: "RBI holds repo rate; stance remains focused on inflation alignment",
    source: "Reuters",
    time: "2h ago",
    tag: "Macro",
  },
  {
    id: "n2",
    title: "SEBI consults on disclosure norms for ESG-labelled funds",
    source: "Economic Times",
    time: "5h ago",
    tag: "Regulation",
  },
  {
    id: "n3",
    title: "FPI flows turn positive for Indian equities this week",
    source: "Bloomberg",
    time: "1d ago",
    tag: "Markets",
  },
  {
    id: "n4",
    title: "Corporate bond primary sees strong appetite for AAA issuers",
    source: "Moneycontrol",
    time: "1d ago",
    tag: "Fixed income",
  },
];

const mockWatchlist: { id: string; name: string; confidence: number; sentiment: string }[] = [
  { id: "1", name: "Reliance Industries", confidence: 0.85, sentiment: "Bullish" },
  { id: "2", name: "TCS", confidence: 0.72, sentiment: "Neutral" },
];

function findEntity(query: string): ResearchEntity | null {
  const q = query.toLowerCase().trim();
  if (q.length < 2) return null;
  const direct = mockResults[q];
  if (direct) return direct;
  for (const [k, v] of Object.entries(mockResults)) {
    if (q.includes(k) || v.name.toLowerCase().includes(q) || (v.ticker && v.ticker.toLowerCase().includes(q))) {
      return v;
    }
  }
  return null;
}

const typeLabel: Record<EntityType, string> = {
  stock: "Stock",
  fund: "Fund / ETF",
  term: "Term",
};

const ResearchPage = () => {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<ResearchEntity | null>(null);
  const [watchlist, setWatchlist] = useState(mockWatchlist);

  const suggestions = useMemo(() => {
    if (query.length < 2) return [] as ResearchEntity[];
    const q = query.toLowerCase();
    return Object.values(mockResults).filter((r) => r.name.toLowerCase().includes(q) || r.key.includes(q) || (r.ticker && r.ticker.toLowerCase().includes(q)));
  }, [query]);

  const runSearch = (q: string) => {
    setQuery(q);
    const hit = findEntity(q);
    setSelected(hit);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Research</h1>
        <p className="text-sm text-muted-foreground mt-1">Latest finance news, plus stocks, funds, and definitions</p>
      </div>

      <Tabs defaultValue="explore" className="w-full">
        <TabsList>
          <TabsTrigger value="explore">Explore</TabsTrigger>
          <TabsTrigger value="news">Latest news</TabsTrigger>
        </TabsList>

        <TabsContent value="news" className="mt-4">
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/30">
              <Newspaper className="w-4 h-4 text-primary" />
              <h2 className="font-semibold text-foreground">Finance headlines</h2>
              <span className="text-xs text-muted-foreground">(demo feed — wire to your news API later)</span>
            </div>
            <ul className="divide-y divide-border">
              {latestNews.map((n) => (
                <li key={n.id} className="px-4 py-3 hover:bg-muted/20 transition flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <div>
                    <p className="text-sm font-medium text-foreground">{n.title}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {n.source} · {n.time}
                    </p>
                  </div>
                  <Badge variant="secondary" className="w-fit">
                    {n.tag}
                  </Badge>
                </li>
              ))}
            </ul>
          </div>
        </TabsContent>

        <TabsContent value="explore" className="mt-4 space-y-6">
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  value={query}
                  onChange={(e) => runSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 rounded-xl border border-input bg-card text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition"
                  placeholder="Search stocks, funds, ETFs, or terms (e.g. Reliance, HDFC Flexi Cap, SIP, ELSS)…"
                />
                {suggestions.length > 0 && !selected && (
                  <div className="absolute top-full left-0 right-0 mt-1 rounded-xl border border-border bg-card shadow-lg z-10 max-h-56 overflow-auto">
                    {suggestions.map((s) => (
                      <button
                        key={s.key}
                        type="button"
                        onClick={() => {
                          setSelected(s);
                          setQuery(s.name);
                        }}
                        className="w-full px-4 py-3 text-left text-sm hover:bg-accent transition flex items-center justify-between gap-2 border-b border-border/50 last:border-0"
                      >
                        <span className="font-medium text-foreground truncate">{s.name}</span>
                        <span className="text-xs text-muted-foreground shrink-0 flex items-center gap-1">
                          <BookOpen className="w-3 h-3" />
                          {typeLabel[s.type]}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <p className="text-xs text-muted-foreground flex flex-wrap gap-2 items-center">
                Try:
                {["HDFC Flexi Cap", "SIP", "Nippon ETF", "Sharpe"].map((t) => (
                  <button
                    key={t}
                    type="button"
                    className="text-primary font-medium hover:underline"
                    onClick={() => runSearch(t)}
                  >
                    {t}
                  </button>
                ))}
              </p>

              {!selected && (
                <div className="rounded-xl border border-border bg-card p-12 text-center">
                  <Search className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground">Search for a stock, mutual fund/ETF, or a finance term to see details</p>
                </div>
              )}

              {selected && (
                <div className="rounded-xl border border-border bg-card p-6 space-y-5 animate-fade-in">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <h2 className="text-xl font-bold text-foreground">{selected.name}</h2>
                        <Badge variant="outline">{typeLabel[selected.type]}</Badge>
                      </div>
                      {selected.ticker && <span className="text-sm text-muted-foreground font-mono">{selected.ticker}</span>}
                    </div>
                    <span
                      className={`flex items-center gap-1 text-sm font-semibold px-3 py-1 rounded-full ${
                        selected.sentiment === "Bullish"
                          ? "bg-success/10 text-success"
                          : selected.sentiment === "Bearish"
                            ? "bg-destructive/10 text-destructive"
                            : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {selected.sentiment === "Bullish" ? <ArrowUpRight className="w-4 h-4" /> : null}
                      {selected.sentiment === "Bearish" ? <ArrowDownRight className="w-4 h-4" /> : null}
                      {selected.sentiment} ({selected.sentiment_score})
                    </span>
                  </div>

                  {selected.extra && <p className="text-sm text-muted-foreground border-l-2 border-primary/40 pl-3">{selected.extra}</p>}

                  <p className="text-sm text-foreground/80 leading-relaxed">{selected.summary}</p>

                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-medium text-muted-foreground">Source confidence</span>
                      <span
                        className={`text-sm font-bold ${
                          selected.confidence > 0.7 ? "text-success" : selected.confidence > 0.4 ? "text-warning" : "text-destructive"
                        }`}
                      >
                        {Math.round(selected.confidence * 100)}%
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          selected.confidence > 0.7 ? "bg-success" : selected.confidence > 0.4 ? "bg-warning" : "bg-destructive"
                        }`}
                        style={{ width: `${selected.confidence * 100}%` }}
                      />
                    </div>
                  </div>

                  {selected.conflict ? (
                    <div className="rounded-lg bg-warning/10 border border-warning/20 p-4 flex gap-3">
                      <AlertTriangle className="w-5 h-5 text-warning shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-foreground">Conflicting signals detected</p>
                        <p className="text-sm text-muted-foreground mt-1">{selected.conflict}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="rounded-lg bg-success/10 border border-success/20 p-3 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-success" />
                      <span className="text-sm text-success font-medium">Sources are consistent</span>
                    </div>
                  )}

                  <div>
                    <p className="text-xs font-medium text-muted-foreground mb-2">Sources</p>
                    <div className="flex flex-wrap gap-2">
                      {selected.sources.map((s) => (
                        <span key={s} className="text-xs px-2.5 py-1 rounded-full bg-muted text-muted-foreground font-medium">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  {selected.type === "stock" && (
                    <button
                      type="button"
                      className="w-full py-2.5 rounded-lg bg-primary/10 text-primary text-sm font-medium hover:bg-primary/20 transition flex items-center justify-center gap-2"
                    >
                      <Plus className="w-4 h-4" /> Add to Watchlist
                    </button>
                  )}
                </div>
              )}
            </div>

            <div className="rounded-xl border border-border bg-card flex flex-col max-h-[520px]">
              <div className="px-5 py-4 border-b border-border">
                <div className="flex items-center gap-2 mb-1">
                  <Star className="w-4 h-4 text-primary" />
                  <h3 className="font-semibold text-foreground">Watchlist</h3>
                </div>
                <p className="text-xs text-muted-foreground">Quick list — same as Research watchlist demo</p>
              </div>
              <ScrollArea className="flex-1 px-5 pb-5">
                <div className="space-y-3 pt-2">
                  {watchlist.map((item) => (
                    <div key={item.id} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                      <div>
                        <p className="text-sm font-medium text-foreground">{item.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs font-medium ${item.confidence > 0.7 ? "text-success" : "text-warning"}`}>
                            {Math.round(item.confidence * 100)}%
                          </span>
                          <span
                            className={`text-xs ${
                              item.sentiment === "Bullish" ? "text-success" : item.sentiment === "Bearish" ? "text-destructive" : "text-muted-foreground"
                            }`}
                          >
                            {item.sentiment}
                          </span>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => setWatchlist(watchlist.filter((w) => w.id !== item.id))}
                        className="text-muted-foreground hover:text-destructive transition"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                  {watchlist.length === 0 && <p className="text-xs text-muted-foreground text-center py-4">No items in watchlist</p>}
                </div>
              </ScrollArea>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ResearchPage;

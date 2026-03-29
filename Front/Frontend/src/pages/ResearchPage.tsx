import React, { useState, useEffect, useRef } from "react";
import { Search, ArrowUpRight, ArrowDownRight, AlertTriangle, CheckCircle, Plus, X, Star, Newspaper, BookOpen, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import client from "@/api/client";

type Company = {
  id: number;
  ticker: string;
  name: string;
  sector: string;
};

type Summary = {
  company_id: number;
  ticker: string;
  company_name: string;
  summary_text: string | null;
  sentiment: string | null;
  sentiment_score: number | null;
  conflict_description: string | null;
  generated_at: string | null;
  message?: string;
};

type WatchlistItem = {
  id: number;
  company_id: number;
  user_id: number;
  added_at: string;
  name?: string;
  ticker?: string;
  sentiment?: string | null;
};

// FIXED: replaces hardcoded latestNews array
type NewsItem = {
  id: string;
  title: string;
  source: string;
  time: string;
  tag: string;
  url?: string;
};

const ResearchPage = () => {
  const { toast } = useToast();
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<Company[]>([]);
  const [selected, setSelected] = useState<Company | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [loadingWatchlist, setLoadingWatchlist] = useState(true);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // FIXED: real news state
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loadingNews, setLoadingNews] = useState(false);
  const [newsError, setNewsError] = useState(false);

  // Load watchlist on mount
  useEffect(() => {
    client.get("/watchlist").then(res => {
      setWatchlist(res.data);
    }).catch(() => { }).finally(() => setLoadingWatchlist(false));
  }, []);

  // FIXED: fetch real news when tab is first opened
  const newsFetched = useRef(false);
  const handleNewsTabOpen = () => {
    if (newsFetched.current) return;
    newsFetched.current = true;
    setLoadingNews(true);
    setNewsError(false);
    client.get("/research/news")
      .then(res => {
        setNews(res.data.articles || []);
      })
      .catch(() => {
        setNewsError(true);
      })
      .finally(() => setLoadingNews(false));
  };

  // Search as user types
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (query.trim().length < 2) { setSuggestions([]); return; }
    debounceRef.current = setTimeout(() => {
      client.get(`/research/search?q=${encodeURIComponent(query)}`).then(res => {
        setSuggestions(res.data.results || []);
      }).catch(() => setSuggestions([]));
    }, 300);
  }, [query]);

  const selectCompany = async (company: Company) => {
    setSelected(company);
    setQuery(company.name);
    setSuggestions([]);
    setSummary(null);
    setLoadingSummary(true);
    try {
      const res = await client.get(`/research/summary/${company.id}`);
      setSummary(res.data);
    } catch {
      setSummary(null);
    } finally {
      setLoadingSummary(false);
    }
  };

  const addToWatchlist = async () => {
    if (!selected) return;
    try {
      const res = await client.post("/watchlist", { company_id: selected.id });
      const enriched = { ...res.data, name: selected.name, ticker: selected.ticker, sentiment: summary?.sentiment };
      setWatchlist(prev => [...prev, enriched]);
      toast({ title: `${selected.name} added to watchlist` });
    } catch (e: any) {
      toast({ title: "Already in watchlist or error occurred", variant: "destructive" });
    }
  };

  const removeFromWatchlist = async (companyId: number) => {
    await client.delete(`/watchlist/${companyId}`).catch(() => { });
    setWatchlist(prev => prev.filter(w => w.company_id !== companyId));
  };

  const sentimentColor = (s: string | null) => {
    if (s === "bullish") return "bg-success/10 text-success";
    if (s === "bearish") return "bg-destructive/10 text-destructive";
    return "bg-muted text-muted-foreground";
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Research</h1>
        <p className="text-sm text-muted-foreground mt-1">AI-powered company intelligence powered by Gemini</p>
      </div>

      <Tabs defaultValue="explore" className="w-full">
        <TabsList>
          <TabsTrigger value="explore">Explore</TabsTrigger>
          {/* FIXED: trigger real fetch when news tab opens */}
          <TabsTrigger value="news" onClick={handleNewsTabOpen}>Latest news</TabsTrigger>
        </TabsList>

        {/* FIXED: news tab now uses real API data */}
        <TabsContent value="news" className="mt-4">
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/30">
              <Newspaper className="w-4 h-4 text-primary" />
              <h2 className="font-semibold text-foreground">Finance headlines</h2>
            </div>

            {/* Loading state */}
            {loadingNews && (
              <div className="flex items-center justify-center gap-3 py-12">
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
                <p className="text-sm text-muted-foreground">Fetching latest news…</p>
              </div>
            )}

            {/* Error state */}
            {!loadingNews && newsError && (
              <div className="flex flex-col items-center justify-center py-12 gap-2">
                <AlertTriangle className="w-6 h-6 text-warning" />
                <p className="text-sm text-muted-foreground">Could not load news. Check that the backend is running.</p>
                <button
                  onClick={() => { newsFetched.current = false; handleNewsTabOpen(); }}
                  className="text-xs text-primary underline mt-1"
                >
                  Retry
                </button>
              </div>
            )}

            {/* Empty state */}
            {!loadingNews && !newsError && news.length === 0 && (
              <div className="flex items-center justify-center py-12">
                <p className="text-sm text-muted-foreground">No news articles found.</p>
              </div>
            )}

            {/* Real news list */}
            {!loadingNews && !newsError && news.length > 0 && (
              <ul className="divide-y divide-border">
                {news.map((n) => (
                  <li key={n.id} className="px-4 py-3 hover:bg-muted/20 transition flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div>
                      {n.url ? (
                        <a href={n.url} target="_blank" rel="noopener noreferrer"
                          className="text-sm font-medium text-foreground hover:text-primary transition">
                          {n.title}
                        </a>
                      ) : (
                        <p className="text-sm font-medium text-foreground">{n.title}</p>
                      )}
                      <p className="text-xs text-muted-foreground mt-1">{n.source} · {n.time}</p>
                    </div>
                    <Badge variant="secondary" className="w-fit">{n.tag}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </TabsContent>

        <TabsContent value="explore" className="mt-4 space-y-6">
          <div className="grid lg:grid-cols-3 gap-6">
            {/* ── Search + Summary Panel ── */}
            <div className="lg:col-span-2 space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  value={query}
                  onChange={(e) => { setQuery(e.target.value); setSelected(null); setSummary(null); }}
                  className="w-full pl-10 pr-4 py-3 rounded-xl border border-input bg-card text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition"
                  placeholder="Search stocks (e.g. Apple, Reliance, INFY, TCS)…"
                />
                {suggestions.length > 0 && !selected && (
                  <div className="absolute top-full left-0 right-0 mt-1 rounded-xl border border-border bg-card shadow-lg z-10 max-h-56 overflow-auto">
                    {suggestions.map((s) => (
                      <button key={s.id} type="button" onClick={() => selectCompany(s)}
                        className="w-full px-4 py-3 text-left text-sm hover:bg-accent transition flex items-center justify-between gap-2 border-b border-border/50 last:border-0">
                        <span className="font-medium text-foreground truncate">{s.name}</span>
                        <span className="text-xs text-muted-foreground shrink-0">{s.ticker} · {s.sector}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {!selected && !loadingSummary && (
                <div className="rounded-xl border border-border bg-card p-12 text-center">
                  <Search className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground">Search for a company to see AI-generated intelligence</p>
                </div>
              )}

              {loadingSummary && (
                <div className="rounded-xl border border-border bg-card p-12 flex items-center justify-center gap-3">
                  <Loader2 className="w-6 h-6 text-primary animate-spin" />
                  <p className="text-sm text-muted-foreground">Fetching AI intelligence…</p>
                </div>
              )}

              {selected && summary && !loadingSummary && (
                <div className="rounded-xl border border-border bg-card p-6 space-y-5">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <h2 className="text-xl font-bold text-foreground">{summary.company_name}</h2>
                        <Badge variant="outline">{selected.sector}</Badge>
                      </div>
                      <span className="text-sm text-muted-foreground font-mono">{summary.ticker}</span>
                    </div>
                    {summary.sentiment && (
                      <span className={`flex items-center gap-1 text-sm font-semibold px-3 py-1 rounded-full ${sentimentColor(summary.sentiment)}`}>
                        {summary.sentiment === "bullish" ? <ArrowUpRight className="w-4 h-4" /> : summary.sentiment === "bearish" ? <ArrowDownRight className="w-4 h-4" /> : null}
                        {summary.sentiment} {summary.sentiment_score != null && `(${summary.sentiment_score}/100)`}
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-foreground/80 leading-relaxed">
                    {summary.summary_text ?? summary.message ?? "No AI summary available yet for this company."}
                  </p>

                  {summary.conflict_description ? (
                    <div className="rounded-lg bg-warning/10 border border-warning/20 p-4 flex gap-3">
                      <AlertTriangle className="w-5 h-5 text-warning shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-foreground">Analyst note</p>
                        <p className="text-sm text-muted-foreground mt-1">{summary.conflict_description}</p>
                      </div>
                    </div>
                  ) : summary.summary_text ? (
                    <div className="rounded-lg bg-success/10 border border-success/20 p-3 flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-success" />
                      <span className="text-sm text-success font-medium">AI sources consistent</span>
                    </div>
                  ) : null}

                  {summary.generated_at && (
                    <p className="text-xs text-muted-foreground">Last generated: {new Date(summary.generated_at).toLocaleString()}</p>
                  )}

                  <button type="button" onClick={addToWatchlist}
                    className="w-full py-2.5 rounded-lg bg-primary/10 text-primary text-sm font-medium hover:bg-primary/20 transition flex items-center justify-center gap-2">
                    <Plus className="w-4 h-4" /> Add to Watchlist
                  </button>
                </div>
              )}
            </div>

            {/* ── Watchlist Sidebar ── */}
            <div className="rounded-xl border border-border bg-card flex flex-col max-h-[520px]">
              <div className="px-5 py-4 border-b border-border">
                <div className="flex items-center gap-2 mb-1">
                  <Star className="w-4 h-4 text-primary" />
                  <h3 className="font-semibold text-foreground">Watchlist</h3>
                </div>
                <p className="text-xs text-muted-foreground">Companies you're tracking</p>
              </div>
              <ScrollArea className="flex-1 px-5 pb-5">
                <div className="space-y-3 pt-2">
                  {loadingWatchlist && (
                    <div className="flex justify-center py-4">
                      <Loader2 className="w-5 h-5 text-primary animate-spin" />
                    </div>
                  )}
                  {!loadingWatchlist && watchlist.map((item) => (
                    <div key={item.id} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                      <div>
                        <p className="text-sm font-medium text-foreground">{item.name ?? `Company #${item.company_id}`}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {item.ticker && <span className="text-xs font-mono text-muted-foreground">{item.ticker}</span>}
                          {item.sentiment && (
                            <span className={`text-xs font-medium ${item.sentiment === "bullish" ? "text-success" : item.sentiment === "bearish" ? "text-destructive" : "text-muted-foreground"}`}>
                              {item.sentiment}
                            </span>
                          )}
                        </div>
                      </div>
                      <button type="button" onClick={() => removeFromWatchlist(item.company_id)}
                        className="text-muted-foreground hover:text-destructive transition">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                  {!loadingWatchlist && watchlist.length === 0 && (
                    <p className="text-xs text-muted-foreground text-center py-4">No items in watchlist</p>
                  )}
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
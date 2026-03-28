import React, { useCallback, useEffect, useRef, useState } from "react";
import { Bot, MessageCircle, Send, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

export type ChatMessage = { id: string; role: "user" | "assistant"; content: string };

/** Dedupes initial challenge handling across React Strict Mode double-mounts. */
const processedChallengeTokens = new Set<string>();

const INTRO =
  "I'm your portfolio AI assistant (demo). Ask what-if scenarios, challenge recommendations, or question predictions. A live model will plug in here later.";

function mockAssistantReply(userText: string, portfolioSummary: string): string {
  const t = userText.toLowerCase();
  if (t.includes("what if") && (t.includes("tech") || t.includes("aapl") || t.includes("googl") || t.includes("msft"))) {
    return "If you cut combined tech (AAPL, GOOGL, MSFT) by 10 percentage points and moved that into investment-grade bonds, expected return might fall roughly 0.8–1.2% annually while volatility could drop ~1.5%. This is illustrative; your actual model will use covariance and forward-looking assumptions.";
  }
  if (t.includes("what if")) {
    return "What-if answers depend on which sleeve you change (equity vs debt vs gold), size of the shift, and horizon. Name the holding or bucket and the change (e.g. “−5% in MSFT, +5% in BONDS”) and I’ll walk through the trade-offs once the engine is connected.";
  }
  if (t.includes("challenge") || t.includes("why ") || t.includes("justify")) {
    return "Recommendations are ranked by risk-adjusted fit to your profile, liquidity, and diversification. If you challenge a specific line item, I’ll cite the main drivers—concentration limits, SEBI-aligned suitability, and volatility budget—once the reasoning API is wired.";
  }
  if (t.includes("prediction") || t.includes("forecast") || t.includes("return")) {
    return "The 14.2% expected return is a model output, not a guarantee. It blends historical regimes and forward assumptions; the backend will expose confidence intervals and stress tests.";
  }
  if (t.includes("sebi") || t.includes("compliance") || t.includes("risky")) {
    return "Compliance checks will flag concentration, unsuitable products, and policy gaps against SEBI norms. Use the dashboard alerts for policy-linked flags; here you can ask how a holding maps to those rules.";
  }
  return `Given your current mix (${portfolioSummary}), I can refine scenarios or explain trade-offs. Try: “What if I reduce tech by 10%?” or “Challenge the bond allocation.”`;
}

type PortfolioFinanceChatProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  portfolioSummary: string;
  initialUserMessage?: string | null;
  /** Unique per challenge so Strict Mode does not duplicate the same prompt. */
  initialMessageToken?: string | null;
  onConsumeInitialMessage?: () => void;
};

export function PortfolioFinanceChat({
  open,
  onOpenChange,
  portfolioSummary,
  initialUserMessage,
  initialMessageToken,
  onConsumeInitialMessage,
}: PortfolioFinanceChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { id: "0", role: "assistant", content: INTRO },
  ]);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  useEffect(() => {
    if (!open || !initialUserMessage || !initialMessageToken) return;
    if (processedChallengeTokens.has(initialMessageToken)) return;
    processedChallengeTokens.add(initialMessageToken);
    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: "user", content: initialUserMessage };
    setMessages((prev) => [...prev, userMsg]);
    const reply = mockAssistantReply(initialUserMessage, portfolioSummary);
    setTimeout(() => {
      setMessages((prev) => [...prev, { id: `a-${Date.now()}`, role: "assistant", content: reply }]);
    }, 400);
    onConsumeInitialMessage?.();
  }, [open, initialUserMessage, initialMessageToken, portfolioSummary, onConsumeInitialMessage]);

  const send = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed) return;
    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    const reply = mockAssistantReply(trimmed, portfolioSummary);
    setTimeout(() => {
      setMessages((prev) => [...prev, { id: `a-${Date.now()}`, role: "assistant", content: reply }]);
    }, 350);
  }, [input, portfolioSummary]);

  return (
    <>
      {!open && (
        <Button
          type="button"
          size="icon"
          className={cn(
            "fixed bottom-6 right-6 z-40 h-14 w-14 rounded-full shadow-lg",
            "bg-primary text-primary-foreground hover:opacity-95",
          )}
          onClick={() => onOpenChange(true)}
          aria-label="Open portfolio AI chat"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      )}

      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent side="right" className="w-full sm:max-w-md flex flex-col p-0 gap-0">
          <SheetHeader className="p-5 pb-2 border-b border-border text-left">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
              <div>
                <SheetTitle className="text-base">Portfolio AI</SheetTitle>
                <SheetDescription className="text-xs">What-if scenarios &amp; explanations (demo)</SheetDescription>
              </div>
            </div>
          </SheetHeader>

          <ScrollArea className="flex-1 min-h-[280px] px-4 py-3">
            <div className="space-y-3 pr-2">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={cn(
                    "flex gap-2",
                    m.role === "user" ? "justify-end" : "justify-start",
                  )}
                >
                  {m.role === "assistant" && (
                    <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <div
                    className={cn(
                      "max-w-[85%] rounded-xl px-3 py-2 text-sm leading-relaxed",
                      m.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground",
                    )}
                  >
                    {m.content}
                  </div>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>
          </ScrollArea>

          <div className="p-4 border-t border-border space-y-2">
            <div className="flex flex-wrap gap-1.5">
              {["What if I cut tech by 10%?", "Challenge bond allocation", "Explain the 14.2% return"].map((q) => (
                <button
                  key={q}
                  type="button"
                  className="text-xs px-2 py-1 rounded-md border border-border bg-background hover:bg-accent transition text-left"
                  onClick={() => {
                    setInput(q);
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a what-if or challenge a recommendation…"
                className="flex-1"
                onKeyDown={(e) => e.key === "Enter" && send()}
              />
              <Button type="button" size="icon" onClick={send} aria-label="Send">
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}

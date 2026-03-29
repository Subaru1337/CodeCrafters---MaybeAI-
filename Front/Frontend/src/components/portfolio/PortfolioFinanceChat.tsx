import React, { useCallback, useEffect, useRef, useState } from "react";
import { Bot, MessageCircle, Send, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";
import client from "@/api/client";

export type ChatMessage = { id: string; role: "user" | "assistant"; content: string };

/** Dedupes initial challenge handling across React Strict Mode double-mounts. */
const processedChallengeTokens = new Set<string>();

const INTRO = "I'm your portfolio AI assistant powered by Gemini. Ask me what-if scenarios, challenge recommendations, or ask about your portfolio allocation.";

type PortfolioFinanceChatProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  portfolioSummary: string;
  initialUserMessage?: string | null;
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
  const [thinking, setThinking] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  // Handle pre-seeded challenge messages (e.g. "Challenge this recommendation")
  useEffect(() => {
    if (!open || !initialUserMessage || !initialMessageToken) return;
    if (processedChallengeTokens.has(initialMessageToken)) return;
    processedChallengeTokens.add(initialMessageToken);
    sendMessage(initialUserMessage);
    onConsumeInitialMessage?.();
  }, [open, initialUserMessage, initialMessageToken]);

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || thinking) return;

    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: "user", content: trimmed };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setThinking(true);

    try {
      const res = await client.post("/chat", { message: trimmed });
      const data = res.data;
      const reply = data.reply ?? "I couldn't generate a response. Please try again.";
      setMessages(prev => [
        ...prev,
        { id: `a-${Date.now()}`, role: "assistant", content: reply },
      ]);

      // If the AI flagged a what-if simulation, log it (frontend can extend this)
      if (data.run_simulation && data.suggested_overrides) {
        console.log("Simulation suggested:", data.suggested_overrides);
      }
    } catch (err: any) {
      const errMsg = err?.response?.data?.detail ?? "Network error — is the API running?";
      setMessages(prev => [
        ...prev,
        { id: `e-${Date.now()}`, role: "assistant", content: `⚠️ ${errMsg}` },
      ]);
    } finally {
      setThinking(false);
    }
  }, [thinking]);

  const send = useCallback(() => {
    sendMessage(input);
  }, [input, sendMessage]);

  const quickPrompts = [
    "What if I cut tech by 10%?",
    "Explain my current allocation",
    "What's my biggest risk?",
  ];

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
                <SheetDescription className="text-xs">Powered by Gemini · What-if scenarios & explanations</SheetDescription>
              </div>
            </div>
          </SheetHeader>

          <ScrollArea className="flex-1 min-h-[280px] px-4 py-3">
            <div className="space-y-3 pr-2">
              {messages.map((m) => (
                <div key={m.id} className={cn("flex gap-2", m.role === "user" ? "justify-end" : "justify-start")}>
                  {m.role === "assistant" && (
                    <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <div className={cn(
                    "max-w-[85%] rounded-xl px-3 py-2 text-sm leading-relaxed",
                    m.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground",
                  )}>
                    {m.content}
                  </div>
                </div>
              ))}

              {thinking && (
                <div className="flex gap-2 justify-start">
                  <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                  <div className="bg-muted rounded-xl px-3 py-2 flex items-center gap-2">
                    <Loader2 className="h-3 w-3 animate-spin text-primary" />
                    <span className="text-sm text-muted-foreground">Thinking…</span>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          </ScrollArea>

          <div className="p-4 border-t border-border space-y-2">
            <div className="flex flex-wrap gap-1.5">
              {quickPrompts.map((q) => (
                <button key={q} type="button"
                  className="text-xs px-2 py-1 rounded-md border border-border bg-background hover:bg-accent transition text-left"
                  onClick={() => sendMessage(q)}>
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
                disabled={thinking}
              />
              <Button type="button" size="icon" onClick={send} disabled={thinking || !input.trim()} aria-label="Send">
                {thinking ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}

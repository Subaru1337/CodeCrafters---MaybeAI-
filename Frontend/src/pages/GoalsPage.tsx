import React, { useMemo, useState } from "react";
import { Target, Plus, TrendingUp, Pencil } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type Goal = {
  id: string;
  name: string;
  target: number;
  current: number;
  deadline: string;
  monthly: number;
  linkedInvestment: string;
};

const seedGoals: Goal[] = [
  { id: "1", name: "Retirement Fund", target: 20000000, current: 5400000, deadline: "2045", monthly: 45000, linkedInvestment: "Equity mutual funds + NPS" },
  { id: "2", name: "Children's Education", target: 5000000, current: 1200000, deadline: "2035", monthly: 25000, linkedInvestment: "Hybrid / debt-heavy mix" },
  { id: "3", name: "Emergency Fund", target: 1500000, current: 1350000, deadline: "2026", monthly: 15000, linkedInvestment: "Liquid funds + sweep FD" },
];

const investmentOptions = [
  "Equity mutual funds",
  "Debt / liquid funds",
  "Direct stocks",
  "NPS / pension",
  "Gold / SGB",
  "Hybrid mix (auto per profile)",
];

const GoalsPage = () => {
  const [goals, setGoals] = useState<Goal[]>(seedGoals);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "",
    target: "",
    current: "",
    deadline: "",
    monthly: "",
    linkedInvestment: investmentOptions[0],
  });

  const resetForm = () => {
    setForm({
      name: "",
      target: "",
      current: "",
      deadline: "",
      monthly: "",
      linkedInvestment: investmentOptions[0],
    });
    setEditingId(null);
  };

  const openNewGoal = () => {
    resetForm();
    setEditingId(null);
    setDialogOpen(true);
  };

  const openEditGoal = (goal: Goal) => {
    setEditingId(goal.id);
    setForm({
      name: goal.name,
      target: String(goal.target),
      current: String(goal.current),
      deadline: goal.deadline,
      monthly: String(goal.monthly),
      linkedInvestment: goal.linkedInvestment,
    });
    setDialogOpen(true);
  };

  const investmentSelectOptions = useMemo(() => {
    const v = form.linkedInvestment.trim();
    if (v && !investmentOptions.includes(v)) return [v, ...investmentOptions];
    return investmentOptions;
  }, [form.linkedInvestment]);

  const saveGoal = (e: React.FormEvent) => {
    e.preventDefault();
    const target = Number(form.target);
    const current = Number(form.current) || 0;
    const monthly = Number(form.monthly);
    if (!form.name.trim() || !form.deadline.trim() || !Number.isFinite(target) || target <= 0 || !Number.isFinite(monthly) || monthly < 0) return;
    const g: Goal = {
      id: editingId ?? `g-${Date.now()}`,
      name: form.name.trim(),
      target,
      current: Math.min(current, target),
      deadline: form.deadline.trim(),
      monthly,
      linkedInvestment: form.linkedInvestment,
    };
    if (editingId) {
      setGoals((prev) => prev.map((x) => (x.id === editingId ? g : x)));
    } else {
      setGoals((prev) => [g, ...prev]);
    }
    setDialogOpen(false);
    resetForm();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Goals</h1>
          <p className="text-sm text-muted-foreground mt-1">Track milestones and tie them to how you invest</p>
        </div>
        <Button onClick={openNewGoal} className="flex items-center gap-1.5">
          <Plus className="w-4 h-4" /> New Goal
        </Button>
      </div>

      <Dialog open={dialogOpen} onOpenChange={(o) => { setDialogOpen(o); if (!o) resetForm(); }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{editingId ? "Edit goal" : "New goal"}</DialogTitle>
            <DialogDescription>Set a target and link it to your investment style. Numbers are stored on the frontend until the API is connected.</DialogDescription>
          </DialogHeader>
          <form onSubmit={saveGoal} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="goal-name">Goal name</Label>
              <Input
                id="goal-name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. Home down payment"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="goal-target">Target amount (₹)</Label>
                <Input
                  id="goal-target"
                  type="number"
                  min={1}
                  step={1000}
                  value={form.target}
                  onChange={(e) => setForm({ ...form, target: e.target.value })}
                  placeholder="5000000"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="goal-current">Current saved (₹)</Label>
                <Input
                  id="goal-current"
                  type="number"
                  min={0}
                  step={1000}
                  value={form.current}
                  onChange={(e) => setForm({ ...form, current: e.target.value })}
                  placeholder="0"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="goal-deadline">Target year</Label>
                <Input
                  id="goal-deadline"
                  value={form.deadline}
                  onChange={(e) => setForm({ ...form, deadline: e.target.value })}
                  placeholder="2032"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="goal-monthly">Monthly investment (₹)</Label>
                <Input
                  id="goal-monthly"
                  type="number"
                  min={0}
                  step={500}
                  value={form.monthly}
                  onChange={(e) => setForm({ ...form, monthly: e.target.value })}
                  placeholder="30000"
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Linked to investments</Label>
              <Select value={form.linkedInvestment} onValueChange={(v) => setForm({ ...form, linkedInvestment: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {investmentSelectOptions.map((o) => (
                    <SelectItem key={o} value={o}>
                      {o}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">{editingId ? "Save changes" : "Create goal"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {goals.map((goal) => {
          const progress = (goal.current / goal.target) * 100;
          return (
            <div key={goal.id} className="rounded-xl border border-border bg-card p-5 space-y-4 hover:glow-green transition-all duration-300">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <h3 className="font-semibold text-foreground">{goal.name}</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">Target by {goal.deadline}</p>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <Button type="button" variant="ghost" size="icon" className="h-9 w-9" onClick={() => openEditGoal(goal)} aria-label={`Edit ${goal.name}`}>
                    <Pencil className="w-4 h-4 text-muted-foreground" />
                  </Button>
                  <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Target className="w-4 h-4 text-primary" />
                  </div>
                </div>
              </div>

              <p className="text-xs text-muted-foreground leading-snug border border-border/60 rounded-lg px-2 py-1.5 bg-muted/30">
                <span className="font-medium text-foreground/90">Investments: </span>
                {goal.linkedInvestment}
              </p>

              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-muted-foreground">₹{(goal.current / 100000).toFixed(1)}L</span>
                  <span className="text-foreground font-medium">₹{(goal.target / 100000).toFixed(0)}L</span>
                </div>
                <div className="h-2 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-primary transition-all duration-500" style={{ width: `${Math.min(progress, 100)}%` }} />
                </div>
                <p className="text-xs text-primary font-medium mt-1">{progress.toFixed(1)}% complete</p>
              </div>

              <div className="flex items-center gap-2 pt-2 border-t border-border/50">
                <TrendingUp className="w-3.5 h-3.5 text-success shrink-0" />
                <span className="text-xs text-muted-foreground">₹{(goal.monthly / 1000).toFixed(0)}K/month</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default GoalsPage;

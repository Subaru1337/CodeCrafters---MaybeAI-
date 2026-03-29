import React, { useMemo, useState, useEffect } from "react";
import { Target, Plus, TrendingUp, Pencil, Trash2, Loader2 } from "lucide-react";
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import client from "@/api/client";

type Goal = {
  id: number;
  goal_name: string;
  target_amount: number;
  initial_capital: number;
  current_value: number;
  target_date: string;
  currency: string;
};

const investmentOptions = [
  "Equity mutual funds",
  "Debt / liquid funds",
  "Direct stocks",
  "NPS / pension",
  "Gold / SGB",
  "Hybrid mix (auto per profile)",
];

const emptyForm = {
  goal_name: "",
  target_amount: "",
  initial_capital: "",
  current_value: "",
  target_date: "",
  currency: "USD",
};

const GoalsPage = () => {
  const { toast } = useToast();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(emptyForm);

  // Fetch goals on mount
  useEffect(() => {
    client.get("/goals")
      .then(res => setGoals(res.data))
      .catch(() => toast({ title: "Failed to load goals", variant: "destructive" }))
      .finally(() => setLoading(false));
  }, []);

  const resetForm = () => { setForm(emptyForm); setEditingId(null); };

  const openNewGoal = () => { resetForm(); setDialogOpen(true); };

  const openEditGoal = (g: Goal) => {
    setEditingId(g.id);
    setForm({
      goal_name: g.goal_name,
      target_amount: String(g.target_amount),
      initial_capital: String(g.initial_capital),
      current_value: String(g.current_value),
      target_date: g.target_date.split("T")[0],
      currency: g.currency,
    });
    setDialogOpen(true);
  };

  const saveGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      goal_name: form.goal_name,
      target_amount: Number(form.target_amount),
      initial_capital: Number(form.initial_capital),
      current_value: Number(form.current_value),
      target_date: form.target_date,
      currency: form.currency,
    };
    setSaving(true);
    try {
      if (editingId) {
        const res = await client.put(`/goals/${editingId}`, payload);
        setGoals(prev => prev.map(g => g.id === editingId ? res.data : g));
        toast({ title: "Goal updated" });
      } else {
        const res = await client.post("/goals", payload);
        setGoals(prev => [res.data, ...prev]);
        toast({ title: "Goal created!" });
      }
      setDialogOpen(false);
      resetForm();
    } catch {
      toast({ title: "Failed to save goal", variant: "destructive" });
    } finally {
      setSaving(false);
    }
  };

  const deleteGoal = async (id: number) => {
    await client.delete(`/goals/${id}`).catch(() => {});
    setGoals(prev => prev.filter(g => g.id !== id));
    toast({ title: "Goal removed" });
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
            <DialogDescription>Set a financial target to track your progress towards.</DialogDescription>
          </DialogHeader>
          <form onSubmit={saveGoal} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="goal-name">Goal name</Label>
              <Input id="goal-name" value={form.goal_name} onChange={(e) => setForm({ ...form, goal_name: e.target.value })} placeholder="e.g. Home down payment" required />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="goal-target">Target amount</Label>
                <Input id="goal-target" type="number" min={1} step={1000} value={form.target_amount} onChange={(e) => setForm({ ...form, target_amount: e.target.value })} placeholder="500000" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="goal-current">Current saved</Label>
                <Input id="goal-current" type="number" min={0} step={1000} value={form.current_value} onChange={(e) => setForm({ ...form, current_value: e.target.value })} placeholder="0" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="goal-initial">Initial capital</Label>
                <Input id="goal-initial" type="number" min={0} step={1000} value={form.initial_capital} onChange={(e) => setForm({ ...form, initial_capital: e.target.value })} placeholder="0" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="goal-deadline">Target date</Label>
                <Input id="goal-deadline" type="date" value={form.target_date} onChange={(e) => setForm({ ...form, target_date: e.target.value })} required />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Currency</Label>
              <Select value={form.currency} onValueChange={(v) => setForm({ ...form, currency: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="USD">USD</SelectItem>
                  <SelectItem value="INR">INR</SelectItem>
                  <SelectItem value="EUR">EUR</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={saving}>{saving ? <Loader2 className="w-4 h-4 animate-spin" /> : editingId ? "Save changes" : "Create goal"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {loading && (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      )}

      {!loading && goals.length === 0 && (
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <Target className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">No goals yet. Create your first financial goal to start tracking!</p>
        </div>
      )}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {goals.map((goal) => {
          const progress = Math.min((goal.current_value / goal.target_amount) * 100, 100);
          return (
            <div key={goal.id} className="rounded-xl border border-border bg-card p-5 space-y-4 hover:shadow-md transition-all duration-300">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <h3 className="font-semibold text-foreground">{goal.goal_name}</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">Target by {new Date(goal.target_date).getFullYear()}</p>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <Button type="button" variant="ghost" size="icon" className="h-8 w-8" onClick={() => openEditGoal(goal)}>
                    <Pencil className="w-3.5 h-3.5 text-muted-foreground" />
                  </Button>
                  <Button type="button" variant="ghost" size="icon" className="h-8 w-8" onClick={() => deleteGoal(goal.id)}>
                    <Trash2 className="w-3.5 h-3.5 text-muted-foreground hover:text-destructive" />
                  </Button>
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Target className="w-4 h-4 text-primary" />
                  </div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-muted-foreground">{goal.currency} {goal.current_value.toLocaleString()}</span>
                  <span className="text-foreground font-medium">{goal.currency} {goal.target_amount.toLocaleString()}</span>
                </div>
                <div className="h-2 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-primary transition-all duration-500" style={{ width: `${progress}%` }} />
                </div>
                <p className="text-xs text-primary font-medium mt-1">{progress.toFixed(1)}% complete</p>
              </div>

              <div className="flex items-center gap-2 pt-2 border-t border-border/50">
                <TrendingUp className="w-3.5 h-3.5 text-success shrink-0" />
                <span className="text-xs text-muted-foreground">Initial capital: {goal.currency} {goal.initial_capital.toLocaleString()}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default GoalsPage;

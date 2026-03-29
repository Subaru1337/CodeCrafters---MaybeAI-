import React, { useMemo, useState, useEffect } from "react";
import { FileUp, Save, CheckCircle, X, FileText, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import client from "@/api/client";

const riskLabels = ["Very Conservative", "Conservative", "Moderate", "Aggressive", "Very Aggressive"];

type UploadedFile = { id: string; name: string; sizeLabel: string; type: string };

type ProfileState = {
  riskLevel: number;
  capital: number;
  currency: string;
  timeHorizon: number;
  taxBracket: string;
  investorType: string;
  targetReturn: number;
  language: string;
  constraints: string[];
};

const defaultProfile: ProfileState = {
  riskLevel: 3,
  capital: 5000000,
  currency: "INR",
  timeHorizon: 5,
  taxBracket: "30%",
  investorType: "Individual",
  targetReturn: 14,
  language: "English",
  constraints: [],
};

const ProfilePage = () => {
  const { toast } = useToast();
  const [profile, setProfile] = useState<ProfileState>(defaultProfile);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [hasExistingProfile, setHasExistingProfile] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  const formatMoney = (n: number, currency: string) =>
    currency === "INR" ? `₹${(n / 100000).toFixed(2)}L` : `${currency} ${n.toLocaleString()}`;

  // ── Load existing profile on mount ──
  useEffect(() => {
    client.get("/profile")
      .then(res => {
        const p = res.data;
        setProfile({
          riskLevel: p.risk_level,
          capital: p.capital_amount,
          currency: "INR",
          timeHorizon: p.time_horizon_years,
          taxBracket: p.tax_bracket ?? "30%",
          investorType: p.investor_type ?? "Individual",
          targetReturn: p.target_return_pct ?? 14,
          language: p.preferred_language ?? "English",
          constraints: p.regulatory_constraints ?? [],
        });
        setHasExistingProfile(true);
        setSavedAt(new Date(p.updated_at).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }));
      })
      .catch(() => {
        // 404 means no profile exists yet — that's fine
        setHasExistingProfile(false);
      })
      .finally(() => setLoading(false));
  }, []);

  // ── Map frontend state → API payload ──
  const toApiPayload = () => ({
    risk_level: profile.riskLevel,
    capital_amount: profile.capital,
    time_horizon_years: profile.timeHorizon,
    tax_bracket: profile.taxBracket,
    investor_type: profile.investorType,
    target_return_pct: profile.targetReturn,
    preferred_language: profile.language,
    regulatory_constraints: profile.constraints,
  });

  // ── Save: POST (first time) or PUT (update) ──
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = toApiPayload();
      if (hasExistingProfile) {
        await client.put("/profile", payload);
      } else {
        await client.post("/profile", payload);
        setHasExistingProfile(true);
      }
      const now = new Date().toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
      setSavedAt(now);
      toast({ title: "Profile saved successfully ✅" });
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Failed to save profile.";
      toast({ title: detail, variant: "destructive" });
    } finally {
      setSaving(false);
    }
  };

  const toggleConstraint = (c: string) => {
    setProfile({
      ...profile,
      constraints: profile.constraints.includes(c)
        ? profile.constraints.filter((x) => x !== c)
        : [...profile.constraints, c],
    });
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files;
    if (!list?.length) return;
    const next: UploadedFile[] = [];
    for (let i = 0; i < list.length; i++) {
      const file = list[i];
      const kb = file.size / 1024;
      next.push({
        id: `${file.name}-${file.size}-${Date.now()}-${i}`,
        name: file.name,
        sizeLabel: kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb.toFixed(0)} KB`,
        type: file.type || "file",
      });
    }
    setUploadedFiles((prev) => [...prev, ...next]);
    e.target.value = "";
  };

  const removeFile = (id: string) => setUploadedFiles((prev) => prev.filter((f) => f.id !== id));

  if (loading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Investor Profile</h1>
        <p className="text-sm text-muted-foreground mt-1">
          {hasExistingProfile ? `Last saved: ${savedAt}` : "Create your profile to unlock portfolio building"}
        </p>
      </div>

      {hasExistingProfile && savedAt && (
        <div className="rounded-lg bg-success/10 border border-success/20 p-3 flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-success" />
          <span className="text-sm text-success font-medium">Profile loaded from database · Last saved {savedAt}</span>
        </div>
      )}

      {/* File upload section */}
      <div className="rounded-xl border border-border bg-card p-6 space-y-4 border-dashed">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            <FileUp className="w-5 h-5 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground">Upload profile documents</p>
            <p className="text-xs text-muted-foreground mt-0.5">PDF, CSV, or images — for reference only</p>
            <label className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm font-medium hover:bg-accent transition">
              <input type="file" className="hidden" accept=".pdf,.csv,.xlsx,.xls,.png,.jpg,.jpeg,.doc,.docx" multiple onChange={onFileChange} />
              Choose files
            </label>
          </div>
        </div>
        {uploadedFiles.length > 0 && (
          <ul className="space-y-2 pt-2 border-t border-border">
            {uploadedFiles.map((f) => (
              <li key={f.id} className="flex items-center justify-between gap-2 rounded-lg border border-border bg-background/50 px-3 py-2 text-sm">
                <span className="truncate font-medium text-foreground">{f.name}</span>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-xs text-muted-foreground">{f.sizeLabel}</span>
                  <button type="button" onClick={() => removeFile(f.id)} className="text-muted-foreground hover:text-destructive p-1">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Profile form */}
      <form onSubmit={handleSave} className="rounded-xl border border-border bg-card p-6 space-y-6">

        {/* Risk Level */}
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Risk Level</label>
          <input type="range" min={1} max={5} value={profile.riskLevel}
            onChange={(e) => setProfile({ ...profile, riskLevel: Number(e.target.value) })}
            className="w-full mt-2 accent-primary" />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            {riskLabels.map((l, i) => (
              <span key={l} className={i + 1 === profile.riskLevel ? "text-primary font-semibold" : ""}>{l}</span>
            ))}
          </div>
        </div>

        {/* Capital + Currency */}
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Capital Amount</label>
            <input type="number" value={profile.capital}
              onChange={(e) => setProfile({ ...profile, capital: Number(e.target.value) })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition" />
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Currency</label>
            <select value={profile.currency} onChange={(e) => setProfile({ ...profile, currency: e.target.value })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition">
              <option>INR</option><option>USD</option>
            </select>
          </div>
        </div>

        {/* Time Horizon + Target Return */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Time Horizon (years)</label>
            <input type="number" min={1} max={50} value={profile.timeHorizon}
              onChange={(e) => setProfile({ ...profile, timeHorizon: Number(e.target.value) })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition" />
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Target Return %</label>
            <input type="number" value={profile.targetReturn}
              onChange={(e) => setProfile({ ...profile, targetReturn: Number(e.target.value) })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition" />
          </div>
        </div>

        {/* Tax Bracket + Investor Type */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Tax Bracket</label>
            <select value={profile.taxBracket} onChange={(e) => setProfile({ ...profile, taxBracket: e.target.value })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition">
              <option>10%</option><option>20%</option><option>30%</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Investor Type</label>
            <select value={profile.investorType} onChange={(e) => setProfile({ ...profile, investorType: e.target.value })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition">
              <option>Individual</option><option>Institution</option><option>Pension Fund</option>
            </select>
          </div>
        </div>

        {/* Regulatory Constraints */}
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Regulatory Constraints</label>
          <div className="mt-2 flex flex-wrap gap-2">
            {["No Crypto", "No Leveraged ETFs", "No Foreign Stocks", "No Options"].map((c) => (
              <button key={c} type="button" onClick={() => toggleConstraint(c)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition ${profile.constraints.includes(c) ? "bg-primary/10 border-primary/30 text-primary" : "border-border text-muted-foreground hover:border-primary/30"}`}>
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Language */}
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Preferred Language</label>
          <select value={profile.language} onChange={(e) => setProfile({ ...profile, language: e.target.value })}
            className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition">
            <option>English</option><option>Hindi</option><option>Tamil</option>
            <option>Telugu</option><option>Spanish</option><option>Arabic</option>
          </select>
        </div>

        <button type="submit" disabled={saving}
          className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition flex items-center justify-center gap-2 disabled:opacity-60">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {saving ? "Saving…" : hasExistingProfile ? "Update Profile" : "Create Profile"}
        </button>
      </form>

      {/* Saved summary cards */}
      {hasExistingProfile && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-foreground">Your saved profile</h2>
            {savedAt && <span className="text-xs text-muted-foreground">Updated {savedAt}</span>}
          </div>
          <div className="grid sm:grid-cols-2 gap-3">
            <Card>
              <CardHeader className="py-3 px-4 pb-0">
                <CardTitle className="text-sm font-medium text-muted-foreground">Risk & horizon</CardTitle>
              </CardHeader>
              <CardContent className="pt-2 px-4 pb-4 space-y-1 text-sm">
                <p><span className="text-muted-foreground">Risk: </span><span className="font-medium">{riskLabels[profile.riskLevel - 1]}</span></p>
                <p><span className="text-muted-foreground">Time horizon: </span><span className="font-medium">{profile.timeHorizon} years</span></p>
                <p><span className="text-muted-foreground">Target return: </span><span className="font-medium">{profile.targetReturn}%</span></p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="py-3 px-4 pb-0">
                <CardTitle className="text-sm font-medium text-muted-foreground">Capital & tax</CardTitle>
              </CardHeader>
              <CardContent className="pt-2 px-4 pb-4 space-y-1 text-sm">
                <p><span className="text-muted-foreground">Capital: </span><span className="font-medium">{formatMoney(profile.capital, profile.currency)}</span></p>
                <p><span className="text-muted-foreground">Currency: </span><span className="font-medium">{profile.currency}</span></p>
                <p><span className="text-muted-foreground">Tax bracket: </span><span className="font-medium">{profile.taxBracket}</span></p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="py-3 px-4 pb-0">
                <CardTitle className="text-sm font-medium text-muted-foreground">Investor</CardTitle>
              </CardHeader>
              <CardContent className="pt-2 px-4 pb-4 space-y-1 text-sm">
                <p><span className="text-muted-foreground">Type: </span><span className="font-medium">{profile.investorType}</span></p>
                <p><span className="text-muted-foreground">Language: </span><span className="font-medium">{profile.language}</span></p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="py-3 px-4 pb-0">
                <CardTitle className="text-sm font-medium text-muted-foreground">Constraints</CardTitle>
              </CardHeader>
              <CardContent className="pt-2 px-4 pb-4 text-sm">
                {profile.constraints.length === 0
                  ? <span className="text-muted-foreground">None selected</span>
                  : <ul className="list-disc list-inside space-y-0.5 text-foreground">{profile.constraints.map(c => <li key={c}>{c}</li>)}</ul>}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;

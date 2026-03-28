import React, { useMemo, useState } from "react";
import { FileUp, Save, CheckCircle, X, FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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
  const [saved, setSaved] = useState(false);
  const [profile, setProfile] = useState<ProfileState>(defaultProfile);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [savedSnapshot, setSavedSnapshot] = useState<{
    profile: ProfileState;
    files: UploadedFile[];
    savedAt: string;
  } | null>(null);

  const formatMoney = (n: number, currency: string) =>
    currency === "INR" ? `₹${(n / 100000).toFixed(2)}L` : `${currency} ${n.toLocaleString()}`;

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSnapshot({
      profile: { ...profile, constraints: [...profile.constraints] },
      files: uploadedFiles.map((f) => ({ ...f })),
      savedAt: new Date().toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }),
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files;
    if (!list?.length) return;
    const next: UploadedFile[] = [];
    for (let i = 0; i < list.length; i++) {
      const file = list[i];
      const kb = file.size / 1024;
      const sizeLabel = kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb.toFixed(0)} KB`;
      next.push({
        id: `${file.name}-${file.size}-${Date.now()}-${i}`,
        name: file.name,
        sizeLabel,
        type: file.type || "file",
      });
    }
    setUploadedFiles((prev) => [...prev, ...next]);
    e.target.value = "";
  };

  const removeFile = (id: string) => setUploadedFiles((prev) => prev.filter((f) => f.id !== id));

  const toggleConstraint = (c: string) => {
    setProfile({
      ...profile,
      constraints: profile.constraints.includes(c) ? profile.constraints.filter((x) => x !== c) : [...profile.constraints, c],
    });
  };

  const summaryBoxes = useMemo(() => {
    if (!savedSnapshot) return null;
    const p = savedSnapshot.profile;
    return (
      <div className="space-y-4 animate-fade-in">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">Saved profile</h2>
          <span className="text-xs text-muted-foreground">Updated {savedSnapshot.savedAt}</span>
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          <Card>
            <CardHeader className="py-3 px-4 pb-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">Risk &amp; horizon</CardTitle>
            </CardHeader>
            <CardContent className="pt-2 px-4 pb-4 space-y-1 text-sm">
              <p>
                <span className="text-muted-foreground">Risk: </span>
                <span className="font-medium text-foreground">{riskLabels[p.riskLevel - 1]}</span>
              </p>
              <p>
                <span className="text-muted-foreground">Time horizon: </span>
                <span className="font-medium text-foreground">{p.timeHorizon} years</span>
              </p>
              <p>
                <span className="text-muted-foreground">Target return: </span>
                <span className="font-medium text-foreground">{p.targetReturn}%</span>
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="py-3 px-4 pb-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">Capital &amp; tax</CardTitle>
            </CardHeader>
            <CardContent className="pt-2 px-4 pb-4 space-y-1 text-sm">
              <p>
                <span className="text-muted-foreground">Capital: </span>
                <span className="font-medium text-foreground">{formatMoney(p.capital, p.currency)}</span>
              </p>
              <p>
                <span className="text-muted-foreground">Currency: </span>
                <span className="font-medium text-foreground">{p.currency}</span>
              </p>
              <p>
                <span className="text-muted-foreground">Tax bracket: </span>
                <span className="font-medium text-foreground">{p.taxBracket}</span>
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="py-3 px-4 pb-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">Investor</CardTitle>
            </CardHeader>
            <CardContent className="pt-2 px-4 pb-4 space-y-1 text-sm">
              <p>
                <span className="text-muted-foreground">Type: </span>
                <span className="font-medium text-foreground">{p.investorType}</span>
              </p>
              <p>
                <span className="text-muted-foreground">Language: </span>
                <span className="font-medium text-foreground">{p.language}</span>
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="py-3 px-4 pb-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">Constraints</CardTitle>
            </CardHeader>
            <CardContent className="pt-2 px-4 pb-4 text-sm">
              {p.constraints.length === 0 ? (
                <span className="text-muted-foreground">None selected</span>
              ) : (
                <ul className="list-disc list-inside space-y-0.5 text-foreground">
                  {p.constraints.map((c) => (
                    <li key={c}>{c}</li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
        <Card>
          <CardHeader className="py-3 px-4 pb-0">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Documents on file
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-2 px-4 pb-4">
            {savedSnapshot.files.length === 0 ? (
              <p className="text-sm text-muted-foreground">No PDF or other files uploaded with this save.</p>
            ) : (
              <ul className="space-y-2">
                {savedSnapshot.files.map((f) => (
                  <li key={f.id} className="flex items-center justify-between text-sm rounded-lg border border-border px-3 py-2">
                    <span className="font-medium text-foreground truncate pr-2">{f.name}</span>
                    <span className="text-xs text-muted-foreground shrink-0">{f.sizeLabel}</span>
                  </li>
                ))}
              </ul>
            )}
            <p className="text-xs text-muted-foreground mt-3">
              Uploads are stored in-browser for this demo; connect storage and parsers when the backend is ready.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }, [savedSnapshot]);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Investor Profile</h1>
        <p className="text-sm text-muted-foreground mt-1">Configure preferences or upload a statement (PDF / file)</p>
      </div>

      {saved && (
        <div className="rounded-lg bg-success/10 border border-success/20 p-3 flex items-center gap-2 animate-fade-in">
          <CheckCircle className="w-4 h-4 text-success" />
          <span className="text-sm text-success font-medium">Profile saved successfully</span>
        </div>
      )}

      <div className="rounded-xl border border-border bg-card p-6 space-y-4 border-dashed">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            <FileUp className="w-5 h-5 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground">Upload profile documents</p>
            <p className="text-xs text-muted-foreground mt-0.5">
              PDF, CSV, or images — for demo, files are listed below; extraction will attach to the backend later.
            </p>
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
                  <button type="button" onClick={() => removeFile(f.id)} className="text-muted-foreground hover:text-destructive p-1" aria-label={`Remove ${f.name}`}>
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <form onSubmit={handleSave} className="rounded-xl border border-border bg-card p-6 space-y-6">
        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Risk Level</label>
          <input
            type="range"
            min={1}
            max={5}
            value={profile.riskLevel}
            onChange={(e) => setProfile({ ...profile, riskLevel: Number(e.target.value) })}
            className="w-full mt-2 accent-primary"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            {riskLabels.map((l, i) => (
              <span key={l} className={i + 1 === profile.riskLevel ? "text-primary font-semibold" : ""}>
                {l}
              </span>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Capital Amount</label>
            <input
              type="number"
              value={profile.capital}
              onChange={(e) => setProfile({ ...profile, capital: Number(e.target.value) })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Currency</label>
            <select
              value={profile.currency}
              onChange={(e) => setProfile({ ...profile, currency: e.target.value })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition"
            >
              <option>INR</option>
              <option>USD</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Time Horizon (years)</label>
            <input
              type="number"
              min={1}
              max={50}
              value={profile.timeHorizon}
              onChange={(e) => setProfile({ ...profile, timeHorizon: Number(e.target.value) })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Target Return %</label>
            <input
              type="number"
              value={profile.targetReturn}
              onChange={(e) => setProfile({ ...profile, targetReturn: Number(e.target.value) })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Tax Bracket</label>
            <select
              value={profile.taxBracket}
              onChange={(e) => setProfile({ ...profile, taxBracket: e.target.value })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition"
            >
              <option>10%</option>
              <option>20%</option>
              <option>30%</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Investor Type</label>
            <select
              value={profile.investorType}
              onChange={(e) => setProfile({ ...profile, investorType: e.target.value })}
              className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition"
            >
              <option>Individual</option>
              <option>Institution</option>
              <option>Pension Fund</option>
            </select>
          </div>
        </div>

        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Regulatory Constraints</label>
          <div className="mt-2 flex flex-wrap gap-2">
            {["No Crypto", "No Leveraged ETFs", "No Foreign Stocks", "No Options"].map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => toggleConstraint(c)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
                  profile.constraints.includes(c) ? "bg-primary/10 border-primary/30 text-primary" : "border-border text-muted-foreground hover:border-primary/30"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Preferred Language</label>
          <select
            value={profile.language}
            onChange={(e) => setProfile({ ...profile, language: e.target.value })}
            className="mt-1.5 w-full px-3 py-2.5 rounded-lg border border-input bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring transition"
          >
            <option>English</option>
            <option>Hindi</option>
            <option>Tamil</option>
            <option>Telugu</option>
            <option>Spanish</option>
            <option>Arabic</option>
          </select>
        </div>

        <button type="submit" className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition flex items-center justify-center gap-2">
          <Save className="w-4 h-4" /> Save Profile
        </button>
      </form>

      {summaryBoxes}
    </div>
  );
};

export default ProfilePage;

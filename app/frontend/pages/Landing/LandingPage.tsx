import { ArrowRight, Bot, FileStack, ShieldAlert, Sparkles, Workflow } from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useAnalysis } from "@/hooks/use-analysis";
import {
  currencyFormatter,
  formatCompactDateTime,
  numberFormatter,
  percentFormatter,
} from "@/utils/formatters";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const featureCards = [
  {
    title: "Dataset-first fraud analysis",
    description:
      "Every workflow is driven by the user’s uploaded CSV or Excel files, not by generic market prediction widgets.",
    icon: FileStack,
  },
  {
    title: "Explainable AI outcomes",
    description:
      "Flagged records are paired with confidence, risk factors, feature impact, and natural-language rationale.",
    icon: ShieldAlert,
  },
  {
    title: "Analyst-ready chatbot",
    description:
      "Investigators can ask focused questions about their dataset, risk concentration, and dashboard findings.",
    icon: Bot,
  },
  {
    title: "Orchestrated pipeline",
    description:
      "Upload, validation, cleaning, fraud scoring, explainability, reporting, and self-learning are staged as a clear workflow.",
    icon: Workflow,
  },
];

const workflow = [
  "Upload Agent",
  "Validation Agent",
  "Cleaning Agent",
  "Preprocessing Agent",
  "Fraud Detection Agent",
  "Explainability Agent",
  "Analytics Agent",
  "Dashboard Agent",
  "Chatbot Agent",
  "Report Agent",
  "Self-Learning Agent",
];

export function LandingPage() {
  const { recentItems, snapshot, transactions } = useAnalysis();
  const totalExposure = transactions
    .filter((item) => item.status === "Fraud")
    .reduce((sum, item) => sum + item.amount, 0);

  return (
    <div className="pb-16">
      <section className="mx-auto grid w-full max-w-7xl gap-12 px-4 pb-10 pt-12 sm:px-6 lg:grid-cols-[1.15fr_0.85fr] lg:px-8 lg:pt-16">
        <div>
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45 }}
            className="inline-flex items-center gap-2 rounded-full border border-border/70 bg-card/70 px-4 py-2 text-xs uppercase tracking-[0.24em] text-muted-foreground shadow-soft backdrop-blur-xl"
          >
            <Sparkles className="h-3.5 w-3.5" />
            IBM Generative AI Internship Project
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.05 }}
            className="mt-8 max-w-4xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl lg:text-6xl"
          >
            GenAI-powered fraud detection for financial datasets your team actually uploads.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.12 }}
            className="mt-6 max-w-2xl text-base leading-8 text-muted-foreground sm:text-lg"
          >
            A clean, enterprise-grade workspace for dataset ingestion, fraud analytics, AI explainability,
            investigation support, and executive reporting. Built to feel production-ready from day one.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.18 }}
            className="mt-8 flex flex-wrap items-center gap-4"
          >
            <Link to="/upload">
              <Button size="lg">
                Start Analysis
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/dashboard">
              <Button size="lg" variant="outline" disabled>
                View Dashboard
              </Button>
            </Link>
          </motion.div>
        </div>

          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.08 }}
            className="grid gap-4"
          >
          <Card className="subtle-grid overflow-hidden">
            <CardContent className="grid gap-6 p-6 sm:grid-cols-2">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Current posture</p>
                <p className="mt-3 text-4xl font-semibold">{snapshot.metrics.riskScore}/100</p>
                <p className="mt-2 text-sm leading-7 text-muted-foreground">
                  Portfolio risk score derived from the current analysis state.
                </p>
              </div>
              <div className="grid gap-4">
                <div className="rounded-2xl border border-border/70 bg-background/50 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Fraud Share</p>
                  <p className="mt-2 text-2xl font-semibold">{percentFormatter.format(snapshot.metrics.fraudRate)}</p>
                </div>
                <div className="rounded-2xl border border-border/70 bg-background/50 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Flagged Exposure</p>
                  <p className="mt-2 text-2xl font-semibold">{currencyFormatter.format(totalExposure)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="grid gap-4 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Workflow</p>
                  <h2 className="mt-2 text-xl font-semibold">Agent pipeline</h2>
                </div>
                <span className="rounded-full bg-primary/8 px-3 py-1 text-xs font-medium text-primary">
                  End-to-end
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {workflow.map((step) => (
                  <span
                    key={step}
                    className="rounded-full border border-border/70 bg-background/50 px-3 py-2 text-xs text-muted-foreground"
                  >
                    {step}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </section>

      <section className="mx-auto mt-6 w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Recent Analysis</p>
            <h2 className="mt-2 text-2xl font-semibold">Latest analysis runs</h2>
          </div>
          <Link to="/upload">
            <Button variant="ghost">Create new run</Button>
          </Link>
        </div>


        <div className="mt-6 grid gap-4 lg:grid-cols-3">
          {recentItems.slice(0, 3).map((item) => (
            <Card key={item.id}>
              <CardContent className="p-6">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                  {formatCompactDateTime(item.createdAt)}
                </p>
                <h3 className="mt-3 text-xl font-semibold">{item.name}</h3>
                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Records</p>
                    <p className="mt-1 text-lg font-semibold">{numberFormatter.format(item.totalRecords)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Fraud Rate</p>
                    <p className="mt-1 text-lg font-semibold">{percentFormatter.format(item.fraudRate)}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Risk</p>
                    <p className="mt-1 text-lg font-semibold">{item.riskScore}/100</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="mx-auto mt-16 w-full max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl">
          <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Platform Features</p>
          <h2 className="mt-2 text-2xl font-semibold">Useful features only, designed for real review workflows</h2>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {featureCards.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title}>
                <CardContent className="p-6">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/8 text-primary">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="mt-5 text-lg font-semibold">{feature.title}</h3>
                  <p className="mt-3 text-sm leading-7 text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      <footer className="mx-auto mt-20 w-full max-w-7xl border-t border-border/70 px-4 pt-8 text-sm text-muted-foreground sm:px-6 lg:px-8">
        <div className="flex flex-col gap-3 pb-8 sm:flex-row sm:items-center sm:justify-between">
          <p>GenAI-Powered Financial Fraud Detection & Analytics Platform</p>
          <p>Frontend-first enterprise experience built for uploaded datasets and explainable review.</p>
        </div>
      </footer>
    </div>
  );
}

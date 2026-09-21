import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  CircleDot,
  LoaderCircle,
  Sparkles,
  Waves,
} from "lucide-react";
import { useAnalysis } from "@/hooks/use-analysis";
import { useToast } from "@/hooks/use-toast";
import { processingSteps } from "@/utils/constants";
import { numberFormatter } from "@/utils/formatters";
import { PageHeading } from "@/components/common/PageHeading";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export function ProcessingPage() {
  const { uploads, snapshot, processingComplete, markProcessingComplete } = useAnalysis();
  const { pushToast } = useToast();
  const [currentIndex, setCurrentIndex] = useState(processingComplete ? processingSteps.length : 1);
  const [isRunning, setIsRunning] = useState(!processingComplete);
  const [completionAnnounced, setCompletionAnnounced] = useState(processingComplete);

  useEffect(() => {
    if (!isRunning) return;

    const intervalId = window.setInterval(() => {
      setCurrentIndex((current) => (current < processingSteps.length ? current + 1 : current));
    }, 850);

    return () => window.clearInterval(intervalId);
  }, [isRunning]);

  useEffect(() => {
    if (currentIndex >= processingSteps.length && isRunning) {
      setIsRunning(false);
      markProcessingComplete(true);
    }
  }, [currentIndex, isRunning, markProcessingComplete]);

  useEffect(() => {
    if (!completionAnnounced && !isRunning && currentIndex >= processingSteps.length) {
      setCompletionAnnounced(true);
      pushToast({
        title: "Analysis prepared",
        description: "Dashboard, chatbot context, and report state are ready.",
        tone: "success",
      });
    }
  }, [completionAnnounced, currentIndex, isRunning, pushToast]);

  const progress = Math.round(
    (Math.min(currentIndex, processingSteps.length) / processingSteps.length) * 100,
  );

  const summaryItems = useMemo(
    () => [
      { label: "Files", value: String(uploads.length || 3) },
      { label: "Estimated Records", value: numberFormatter.format(snapshot.metrics.totalRecords) },
      { label: "Projected Risk Score", value: `${snapshot.metrics.riskScore}/100` },
    ],
    [snapshot.metrics.riskScore, snapshot.metrics.totalRecords, uploads.length],
  );

  return (
    <div className="space-y-8">
      <PageHeading
        eyebrow="Processing"
        title="The AI workflow is building your analysis workspace"
        description="Validation, cleaning, risk scoring, explainability, dashboard generation, chatbot preparation, and report assembly run through a professional step pipeline."
        actions={
          processingComplete ? (
            <Link to="/dashboard">
              <Button>
                Open Dashboard
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          ) : null
        }
      />

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <CardHeader>
            <CardTitle>Pipeline execution</CardTitle>
            <CardDescription>Each stage advances the dataset from raw upload to investigation-ready output.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Overall progress</span>
                <span className="font-medium">{progress}%</span>
              </div>
              <Progress value={progress} className="h-3" />
            </div>

            <div className="space-y-3">
              {processingSteps.map((step, index) => {
                const isCompleted = index < currentIndex || processingComplete;
                const isActive = index === currentIndex && isRunning;

                return (
                  <div
                    key={step.id}
                    className={`rounded-2xl border p-4 transition ${
                      isActive
                        ? "border-primary/35 bg-primary/6 shadow-soft"
                        : isCompleted
                          ? "border-emerald-500/20 bg-emerald-500/6"
                          : "border-border/70 bg-background/40"
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div className="mt-0.5">
                        {isCompleted ? (
                          <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                        ) : isActive ? (
                          <LoaderCircle className="h-5 w-5 animate-spin text-primary" />
                        ) : (
                          <CircleDot className="h-5 w-5 text-muted-foreground" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{step.title}</p>
                        <p className="mt-1 text-sm leading-6 text-muted-foreground">{step.detail}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card className="overflow-hidden">
            <CardHeader>
              <CardTitle>AI working state</CardTitle>
              <CardDescription>Designed to make the analysis feel active and trustworthy.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="rounded-[28px] border border-border/70 bg-background/50 p-5">
                <div className="flex items-center gap-3">
                  <div className="rounded-2xl bg-primary/10 p-3 text-primary">
                    <Sparkles className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-medium">Signal enrichment in progress</p>
                    <p className="text-sm text-muted-foreground">Temporal, behavioral, and entity-level signals are being assembled.</p>
                  </div>
                </div>
                <div className="mt-6 space-y-3">
                  {[1, 2, 3].map((item) => (
                    <div key={item} className="h-2.5 rounded-full bg-secondary">
                      <div
                        className="h-full rounded-full bg-primary animate-pulseLine"
                        style={{ width: `${72 + item * 7}%` }}
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                {summaryItems.map((item) => (
                  <div key={item.label} className="rounded-2xl border border-border/70 bg-background/40 p-4">
                    <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{item.label}</p>
                    <p className="mt-2 text-2xl font-semibold">{item.value}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Generated outputs</CardTitle>
              <CardDescription>The same pipeline prepares downstream analyst experiences.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                "Interactive dashboard with filters and charts",
                "Record-level explainability and AI rationale",
                "Chatbot context restricted to uploaded data",
                "Executive report with export actions",
              ].map((item) => (
                <div key={item} className="flex items-center gap-3 rounded-2xl border border-border/70 bg-background/40 p-4">
                  <Waves className="h-4 w-4 text-primary" />
                  <span className="text-sm">{item}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

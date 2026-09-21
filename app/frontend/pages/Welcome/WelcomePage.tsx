import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck, UploadCloud } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAnalysis } from "@/hooks/use-analysis";

export function WelcomePage() {
  const { uploads, processingComplete } = useAnalysis();

  const cta = processingComplete ? (
    <Link to="/dashboard">
      <Button size="lg">
        View Dashboard
        <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </Link>
  ) : uploads.length > 0 ? (
    <Link to="/processing">
      <Button size="lg">
        Continue Processing
        <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </Link>
  ) : (
    <Link to="/upload">
      <Button size="lg">
        Start Analysis
        <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </Link>
  );

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-10 px-4 pb-16 pt-10 sm:px-6 lg:pt-14">
      <div className="flex flex-col items-start justify-between gap-8 lg:flex-row lg:items-end">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="max-w-2xl"
        >
          <div className="inline-flex items-center gap-3 rounded-full border border-border/70 bg-card/70 px-4 py-2 text-sm shadow-soft backdrop-blur-xl">
            <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <span className="font-medium">Dataset-driven fraud detection</span>
          </div>

          <h1 className="mt-7 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
            Welcome to your enterprise fraud analytics workspace
          </h1>
          <p className="mt-4 text-muted-foreground">
            Upload your CSV/XLSX files. The workflow validates data, detects fraud patterns, and generates
            explainable outputs for analysts.
          </p>
        </motion.div>

        <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:items-center">
          {cta}
          <Link to="/upload" className="w-full sm:w-auto">
            <Button variant="outline" size="lg" className="w-full sm:w-auto">
              Upload Datasets
              <UploadCloud className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {[
          {
            title: "Explainable fraud outcomes",
            desc: "Every flagged record includes confidence, risk factors, affected features, and rationale.",
          },
          {
            title: "Analyst-ready dashboard",
            desc: "Risk posture, category concentration, amount spread, and timeline analysis update from your files.",
          },
          {
            title: "Dataset-restricted chat",
            desc: "Ask questions only about the uploaded dataset and receive grounded summaries.",
          },
        ].map((item) => (
          <motion.div
            key={item.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.05 }}
            className="animate-soft-float"
          >
            <Card>
              <CardContent className="p-6">
                <h3 className="text-base font-semibold">{item.title}</h3>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">{item.desc}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}


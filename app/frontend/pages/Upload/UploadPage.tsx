import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, CheckCircle2, FolderInput } from "lucide-react";
import { useAnalysis } from "@/hooks/use-analysis";
import { useToast } from "@/hooks/use-toast";
import { PageHeading } from "@/components/common/PageHeading";
import { DatasetSummaryCard } from "@/components/upload/DatasetSummaryCard";
import { FileDropzone } from "@/components/upload/FileDropzone";
import { FilePreviewTable } from "@/components/upload/FilePreviewTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";

const uploadSchema = z.object({
  analysisName: z.string().min(3, "Analysis name should be at least 3 characters."),
  ownerEmail: z.string().email("Enter a valid analyst email."),
  notes: z.string().max(240, "Keep notes within 240 characters.").optional(),
});

type UploadFormValues = z.infer<typeof uploadSchema>;

export function UploadPage() {
  const navigate = useNavigate();
  const { uploads, isUploading, uploadFiles } = useAnalysis();
  const { pushToast } = useToast();
  const [progress, setProgress] = useState(0);

  const form = useForm<UploadFormValues>({
    resolver: zodResolver(uploadSchema),
    defaultValues: {
      analysisName: "July financial fraud review",
      ownerEmail: "analyst@company.com",
      notes: "Focus on high-value transfers and invoice payment behavior.",
    },
  });

  async function handleFilesSelected(files: File[]) {
    const intervalId = window.setInterval(() => {
      setProgress((current) => (current >= 92 ? current : current + 8));
    }, 120);

    try {
      await uploadFiles(files);
      setProgress(100);
      pushToast({
        title: "Upload complete",
        description: `${files.length} file(s) were parsed and staged for analysis.`,
        tone: "success",
      });
    } finally {
      window.clearInterval(intervalId);
      window.setTimeout(() => setProgress(0), 900);
    }
  }

  function continueToProcessing() {
    navigate("/processing");
  }

  return (
    <div className="space-y-8">
      <PageHeading
        eyebrow="Upload"
        title="Bring in the dataset that should be analyzed"
        description="CSV and Excel uploads are parsed client-side to validate structure, preview rows, and prepare the analysis pipeline."
        actions={
          <Button onClick={continueToProcessing} disabled={uploads.length === 0}>
            Continue
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        }
      />

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader>
            <CardTitle>Upload dataset</CardTitle>
            <CardDescription>Drop one or many files. Validation and preview happen before processing starts.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <FileDropzone onFilesSelected={handleFilesSelected} isBusy={isUploading} />
            {progress > 0 ? (
              <div className="space-y-3 rounded-2xl border border-border/70 bg-background/40 p-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Upload progress</span>
                  <span className="font-medium">{progress}%</span>
                </div>
                <Progress value={progress} />
              </div>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Analysis configuration</CardTitle>
            <CardDescription>Capture basic metadata for the current review run.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium">Analysis name</label>
                <Input {...form.register("analysisName")} placeholder="Quarterly fraud review" />
                <p className="mt-2 text-xs text-danger">{form.formState.errors.analysisName?.message}</p>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">Owner email</label>
                <Input {...form.register("ownerEmail")} placeholder="analyst@company.com" />
                <p className="mt-2 text-xs text-danger">{form.formState.errors.ownerEmail?.message}</p>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">Review notes</label>
                <Textarea {...form.register("notes")} placeholder="Any special focus for this run" />
                <p className="mt-2 text-xs text-danger">{form.formState.errors.notes?.message}</p>
              </div>

              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/8 p-4">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-500" />
                  <div>
                    <p className="font-medium">Ready for multi-file analysis</p>
                    <p className="mt-1 text-sm leading-6 text-muted-foreground">
                      Uploads support CSV and Excel formats with preview, schema detection, and validation messaging.
                    </p>
                  </div>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>

      {uploads.length > 0 ? (
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <FolderInput className="h-5 w-5 text-primary" />
            <h2 className="text-xl font-semibold">Dataset preview</h2>
          </div>

          {uploads.map((dataset) => (
            <div key={dataset.id} className="space-y-4">
              <DatasetSummaryCard dataset={dataset} />
              <FilePreviewTable dataset={dataset} />
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

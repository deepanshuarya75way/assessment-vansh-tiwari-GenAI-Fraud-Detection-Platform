import { useRef, useState } from "react";
import { FileSpreadsheet, UploadCloud } from "lucide-react";
import { cn } from "@/utils/cn";
import { Button } from "@/components/ui/button";

interface FileDropzoneProps {
  onFilesSelected: (files: File[]) => void;
  isBusy?: boolean;
}

export function FileDropzone({ onFilesSelected, isBusy }: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  function handleFileList(fileList: FileList | null) {
    if (!fileList) return;
    onFilesSelected(Array.from(fileList));
  }

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        handleFileList(event.dataTransfer.files);
      }}
      className={cn(
        "rounded-[28px] border border-dashed p-8 text-center transition",
        isDragging
          ? "border-primary bg-primary/5 shadow-soft"
          : "border-border bg-card/60 hover:border-foreground/20 hover:bg-card/80",
      )}
    >
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-primary/8 text-primary">
        {isDragging ? <UploadCloud className="h-8 w-8" /> : <FileSpreadsheet className="h-8 w-8" />}
      </div>
      <h3 className="mt-6 text-xl font-semibold">Drop CSV or Excel files here</h3>
      <p className="mx-auto mt-3 max-w-2xl text-sm leading-7 text-muted-foreground">
        Upload one or more datasets. Client-side parsing reads schema, row count, and preview rows
        before the analysis workflow begins.
      </p>
      <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
        <Button onClick={() => inputRef.current?.click()} disabled={isBusy}>
          Select Files
        </Button>
        <Button variant="outline" disabled>
          Supports CSV, XLSX, XLS
        </Button>
      </div>
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".csv,.xlsx,.xls"
        className="hidden"
        onChange={(event) => handleFileList(event.target.files)}
      />
    </div>
  );
}

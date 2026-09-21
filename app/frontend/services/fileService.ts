import * as XLSX from "xlsx";
import type { UploadedDataset } from "@/utils/types";

function normalizeCell(value: unknown) {
  if (value === undefined || value === null) return "";
  return String(value);
}

export async function parseUploadedFiles(files: File[]): Promise<UploadedDataset[]> {
  return Promise.all(
    files.map(async (file) => {
      const buffer = await file.arrayBuffer();
      const workbook = XLSX.read(buffer, { type: "array" });
      const firstSheet = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[firstSheet];
      const rows = XLSX.utils.sheet_to_json<(string | number | null)[]>(worksheet, {
        header: 1,
        blankrows: false,
      });

      const [headerRow = [], ...dataRows] = rows;
      const preview = dataRows.slice(0, 5).map((row) => row.map(normalizeCell));
      const columns = headerRow.map(normalizeCell).filter(Boolean);
      const extension = file.name.split(".").pop()?.toLowerCase();
      const isSupported = ["csv", "xlsx", "xls"].includes(extension ?? "");

      return {
        id: crypto.randomUUID(),
        name: file.name,
        size: file.size,
        type: file.type || extension || "unknown",
        uploadedAt: new Date().toISOString(),
        rows: dataRows.length,
        columns,
        preview,
        validation: {
          status: isSupported ? "valid" : "warning",
          message: isSupported
            ? "Dataset structure is readable and ready for analysis."
            : "Unsupported file extension detected.",
        },
      } satisfies UploadedDataset;
    }),
  );
}

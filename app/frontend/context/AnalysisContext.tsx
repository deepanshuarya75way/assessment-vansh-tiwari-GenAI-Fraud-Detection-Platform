import {
  createContext,
  type PropsWithChildren,
  useMemo,
  useState,
} from "react";
import { answerQuestion } from "@/services/chatbotService";
import { parseUploadedFiles } from "@/services/fileService";
import { createDashboardSnapshot, deriveTransactionsFromUploads } from "@/services/sessionAnalytics";
import type {
  AnalysisSummary,
  ChatMessage,
  DashboardSnapshot,
  FraudFilters,
  TransactionRecord,
  UploadedDataset,
} from "@/utils/types";

interface AnalysisContextValue {
  uploads: UploadedDataset[];
  isUploading: boolean;
  processingComplete: boolean;
  transactions: TransactionRecord[];
  snapshot: DashboardSnapshot;
  filters: FraudFilters;
  messages: ChatMessage[];
  recentItems: AnalysisSummary[];
  setFilters: (filters: Partial<FraudFilters>) => void;
  uploadFiles: (files: File[]) => Promise<void>;
  markProcessingComplete: (value: boolean) => void;
  addChatMessage: (message: string) => void;
}

const defaultFilters: FraudFilters = {
  search: "",
  category: "All",
  status: "All",
  risk: "All",
  dateRange: "30",
  minAmount: 0,
  maxAmount: 25000,
};

const initialMessages: ChatMessage[] = [
  {
    id: "assistant-welcome",
    role: "assistant",
    createdAt: new Date().toISOString(),
    content:
      "I can answer questions about the active session, fraud concentration, high-risk transactions, and the latest analytics snapshot.",
  },
];

export const AnalysisContext = createContext<AnalysisContextValue | null>(null);

export function AnalysisProvider({ children }: PropsWithChildren) {
  const [uploads, setUploads] = useState<UploadedDataset[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [processingComplete, setProcessingComplete] = useState(false);
  const [filters, setFiltersState] = useState<FraudFilters>(defaultFilters);
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [recentItems, setRecentItems] = useState<AnalysisSummary[]>([]);

  const transactions = useMemo<TransactionRecord[]>(() => {
    if (uploads.length === 0) {
      return [];
    }
    return deriveTransactionsFromUploads(uploads);
  }, [uploads]);

  const snapshot = useMemo<DashboardSnapshot>(() => {
    return createDashboardSnapshot(uploads, transactions, uploads[0]?.name);
  }, [uploads, transactions]);

  async function uploadFiles(files: File[]) {
    setIsUploading(true);
    const parsedFiles = await parseUploadedFiles(files);
    const nextTransactions = deriveTransactionsFromUploads(parsedFiles);
    const nextSnapshot = createDashboardSnapshot(parsedFiles, nextTransactions, files[0]?.name);
    setUploads(parsedFiles);
    setRecentItems((current) => [
      {
        id: crypto.randomUUID(),
        name: files.length > 1 ? "Multi-file uploaded dataset" : files[0]?.name ?? "Uploaded dataset",
        createdAt: new Date().toISOString(),
        totalRecords: parsedFiles.reduce((total, item) => total + item.rows, 0),
        fraudRate: nextSnapshot.metrics.fraudRate,
        riskScore: nextSnapshot.metrics.riskScore,
        files: parsedFiles.length,
      },
      ...current,
    ]);
    setProcessingComplete(false);
    setIsUploading(false);
  }

  function setFilters(nextFilters: Partial<FraudFilters>) {
    setFiltersState((current) => ({ ...current, ...nextFilters }));
  }

  function markProcessingComplete(value: boolean) {
    setProcessingComplete(value);
  }

  function addChatMessage(message: string) {
    const createdAt = new Date().toISOString();
    const assistantReply = answerQuestion(message, snapshot, transactions);
    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", content: message, createdAt },
      {
        id: crypto.randomUUID(),
        role: "assistant",
        content: assistantReply,
        createdAt: new Date().toISOString(),
      },
    ]);
  }

  const value = useMemo(
    () => ({
      uploads,
      isUploading,
      processingComplete,
      transactions,
      snapshot,
      filters,
      messages,
      recentItems,
      setFilters,
      uploadFiles,
      markProcessingComplete,
      addChatMessage,
    }),
    [uploads, isUploading, processingComplete, transactions, snapshot, filters, messages, recentItems],
  );

  return <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>;
}

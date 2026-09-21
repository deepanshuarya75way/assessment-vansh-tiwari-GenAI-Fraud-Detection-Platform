import {
  Bot,
  ChartNoAxesCombined,
  FileCog,
  FileSpreadsheet,
  LayoutDashboard,
  Settings,
  ShieldAlert,
  Upload,
} from "lucide-react";
import type { ProcessingStep } from "@/utils/types";

export const appNavigation = [
  { label: "Upload", href: "/upload", icon: Upload },
  { label: "Processing", href: "/processing", icon: FileCog },
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Fraud Details", href: "/dashboard/fraud-details", icon: ShieldAlert },
  {
    label: "Explainability",
    href: "/dashboard/explainability",
    icon: ChartNoAxesCombined,
  },
  { label: "AI Chatbot", href: "/chatbot", icon: Bot },
  { label: "AI Report", href: "/reports", icon: FileSpreadsheet },
  { label: "Settings", href: "/settings", icon: Settings },
];

export const processingSteps: ProcessingStep[] = [
  {
    id: "upload",
    title: "Upload Complete",
    detail: "Files were staged successfully and encrypted at rest.",
  },
  {
    id: "reading",
    title: "Reading Dataset",
    detail: "Column schema, formats, and sample windows are being loaded.",
  },
  {
    id: "validation",
    title: "Data Validation",
    detail: "File integrity, type constraints, and schema consistency are being checked.",
  },
  {
    id: "missing",
    title: "Missing Value Detection",
    detail: "Sparse fields and null-heavy attributes are being profiled.",
  },
  {
    id: "duplicate",
    title: "Duplicate Detection",
    detail: "Near-duplicate transactions and repeated identifiers are being resolved.",
  },
  {
    id: "cleaning",
    title: "Data Cleaning",
    detail: "Amounts, timestamps, labels, and channel values are being normalized.",
  },
  {
    id: "engineering",
    title: "Feature Engineering",
    detail: "Behavioral, temporal, and merchant risk signals are being created.",
  },
  {
    id: "fraud",
    title: "Fraud Detection",
    detail: "Suspicious transaction clusters and anomalous risk signals are being scored.",
  },
  {
    id: "risk",
    title: "Risk Analysis",
    detail: "Fraud density, confidence, and exposure levels are being summarized.",
  },
  {
    id: "insights",
    title: "AI Insight Generation",
    detail: "Findings and contextual explanations are being written for business users.",
  },
  {
    id: "dashboard",
    title: "Dashboard Generation",
    detail: "Metrics, filters, trends, and fraud tables are being assembled.",
  },
  {
    id: "chatbot",
    title: "Chatbot Preparation",
    detail: "Dataset-specific retrieval context is being indexed for questions.",
  },
  {
    id: "report",
    title: "Report Preparation",
    detail: "Executive summary, charts, and export bundles are being compiled.",
  },
];

export const suggestedQuestions = [
  "What is the total fraud?",
  "Show highest risk transactions.",
  "Which category contains maximum fraud?",
  "Explain this dashboard.",
];

import { BotMessageSquare, Database, MessagesSquare } from "lucide-react";
import { useAnalysis } from "@/hooks/use-analysis";
import { PageHeading } from "@/components/common/PageHeading";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { Card, CardContent } from "@/components/ui/card";
import { numberFormatter } from "@/utils/formatters";

export function ChatbotPage() {
  const { snapshot, uploads } = useAnalysis();

  return (
    <div className="space-y-8">
      <PageHeading
        eyebrow="AI Chatbot"
        title="Ask the dataset questions in a focused conversational workspace"
        description="The assistant is designed to respond only to the uploaded dataset, current dashboard state, and fraud analysis context."
      />

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="flex items-center gap-4 p-6">
            <div className="rounded-2xl bg-primary/8 p-3 text-primary">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Current records</p>
              <p className="mt-1 text-2xl font-semibold">{numberFormatter.format(snapshot.metrics.totalRecords)}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-6">
            <div className="rounded-2xl bg-primary/8 p-3 text-primary">
              <BotMessageSquare className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Dataset scope</p>
              <p className="mt-1 text-2xl font-semibold">{uploads.length || 3} files</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-6">
            <div className="rounded-2xl bg-primary/8 p-3 text-primary">
              <MessagesSquare className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Answer mode</p>
              <p className="mt-1 text-2xl font-semibold">Dataset-only</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <ChatWindow />
    </div>
  );
}

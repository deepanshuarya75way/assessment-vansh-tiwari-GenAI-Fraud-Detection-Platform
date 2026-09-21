import { useState } from "react";
import { Sparkles } from "lucide-react";
import { useAnalysis } from "@/hooks/use-analysis";
import { suggestedQuestions } from "@/utils/constants";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { formatCompactDateTime } from "@/utils/formatters";

export function ChatWindow() {
  const [draft, setDraft] = useState("");
  const { messages, addChatMessage } = useAnalysis();

  function submitMessage(message: string) {
    if (!message.trim()) return;
    addChatMessage(message.trim());
    setDraft("");
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
      <Card className="h-fit">
        <CardHeader>
          <CardTitle>Suggested Questions</CardTitle>
          <CardDescription>Ask only about the uploaded dataset and generated analysis.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {suggestedQuestions.map((question) => (
            <button
              key={question}
              type="button"
              onClick={() => submitMessage(question)}
              className="w-full rounded-2xl border border-border/70 bg-background/40 px-4 py-3 text-left text-sm transition hover:border-foreground/20 hover:bg-accent"
            >
              {question}
            </button>
          ))}
        </CardContent>
      </Card>

      <Card className="flex min-h-[620px] flex-col">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-primary/8 p-3 text-primary">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <CardTitle>Dataset Intelligence Assistant</CardTitle>
              <CardDescription>
                Answers are constrained to the current uploaded data and analysis state.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex flex-1 flex-col gap-4">
          <div className="flex-1 space-y-4 overflow-y-auto rounded-2xl border border-border/70 bg-background/35 p-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                  message.role === "assistant"
                    ? "bg-secondary text-secondary-foreground"
                    : "ml-auto bg-primary text-primary-foreground"
                }`}
              >
                <p className="text-sm leading-7">{message.content}</p>
                <p className="mt-2 text-[11px] uppercase tracking-[0.2em] opacity-70">
                  {formatCompactDateTime(message.createdAt)}
                </p>
              </div>
            ))}
          </div>
          <div className="flex gap-3">
            <Input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask about fraud totals, high-risk transactions, categories, or dashboard insights"
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  submitMessage(draft);
                }
              }}
            />
            <Button onClick={() => submitMessage(draft)}>Send</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

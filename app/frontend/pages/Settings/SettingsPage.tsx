import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Bell, ShieldCheck, UserRound } from "lucide-react";
import { useTheme } from "@/hooks/use-theme";
import { useToast } from "@/hooks/use-toast";
import { PageHeading } from "@/components/common/PageHeading";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

const settingsSchema = z.object({
  fullName: z.string().min(2, "Name is required."),
  email: z.string().email("Enter a valid email."),
  workspace: z.string().min(2, "Workspace name is required."),
  theme: z.enum(["light", "dark"]),
  notificationDigest: z.boolean(),
  criticalAlerts: z.boolean(),
});

type SettingsValues = z.infer<typeof settingsSchema>;

export function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { pushToast } = useToast();

  const form = useForm<SettingsValues>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      fullName: "Fraud Analyst",
      email: "analyst@company.com",
      workspace: "Financial Risk Operations",
      theme,
      notificationDigest: true,
      criticalAlerts: true,
    },
  });

  function onSubmit(values: SettingsValues) {
    setTheme(values.theme);
    pushToast({
      title: "Settings updated",
      description: "Theme, profile, and notification preferences were saved locally.",
      tone: "success",
    });
  }

  return (
    <div className="space-y-8">
      <PageHeading
        eyebrow="Settings"
        title="Manage workspace preferences"
        description="Theme, analyst profile, notifications, and product information are centralized here."
      />

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader>
            <CardTitle>Profile and preferences</CardTitle>
            <CardDescription>These settings shape the current frontend workspace experience.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium">Full name</label>
                <Input {...form.register("fullName")} />
                <p className="mt-2 text-xs text-danger">{form.formState.errors.fullName?.message}</p>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">Email</label>
                <Input {...form.register("email")} />
                <p className="mt-2 text-xs text-danger">{form.formState.errors.email?.message}</p>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">Workspace</label>
                <Input {...form.register("workspace")} />
                <p className="mt-2 text-xs text-danger">{form.formState.errors.workspace?.message}</p>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">Theme</label>
                <Select {...form.register("theme")}>
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </Select>
              </div>

              <div className="space-y-3">
                <label className="flex items-center gap-3 rounded-2xl border border-border/70 bg-background/40 p-4">
                  <input type="checkbox" className="h-4 w-4" {...form.register("notificationDigest")} />
                  <div>
                    <p className="font-medium">Weekly digest</p>
                    <p className="text-sm text-muted-foreground">Receive a summary of fraud trends and analysis runs.</p>
                  </div>
                </label>

                <label className="flex items-center gap-3 rounded-2xl border border-border/70 bg-background/40 p-4">
                  <input type="checkbox" className="h-4 w-4" {...form.register("criticalAlerts")} />
                  <div>
                    <p className="font-medium">Critical risk alerts</p>
                    <p className="text-sm text-muted-foreground">Highlight severe fraud spikes and risky transaction clusters.</p>
                  </div>
                </label>
              </div>

              <Button type="submit">Save preferences</Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>About this frontend</CardTitle>
              <CardDescription>Implementation details for the current project delivery.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                {
                  title: "Frontend Stack",
                  description: "React 19, Vite, TypeScript, Tailwind CSS, Framer Motion, Recharts, React Hook Form, and Zod.",
                  icon: ShieldCheck,
                },
                {
                  title: "Interaction Model",
                  description: "Mocked services simulate dataset analysis, explainability, chatbot answers, and reporting until backend integration.",
                  icon: Bell,
                },
                {
                  title: "Workspace Design",
                  description: "Enterprise-grade, responsive, minimal, and purpose-built for uploaded financial data investigations.",
                  icon: UserRound,
                },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.title} className="rounded-2xl border border-border/70 bg-background/40 p-4">
                    <div className="flex items-start gap-3">
                      <div className="rounded-2xl bg-primary/8 p-3 text-primary">
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="font-medium">{item.title}</p>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.description}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

import {
  createContext,
  type PropsWithChildren,
  useCallback,
  useMemo,
  useState,
} from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Info, TriangleAlert } from "lucide-react";
import { cn } from "@/utils/cn";

type ToastTone = "success" | "info" | "warning";

interface ToastItem {
  id: string;
  title: string;
  description: string;
  tone: ToastTone;
}

interface ToastContextValue {
  pushToast: (toast: Omit<ToastItem, "id">) => void;
}

export const ToastContext = createContext<ToastContextValue | null>(null);

const toneStyles: Record<ToastTone, string> = {
  success: "border-emerald-500/25 bg-emerald-500/10 text-emerald-200",
  info: "border-sky-500/25 bg-sky-500/10 text-sky-200",
  warning: "border-amber-500/25 bg-amber-500/10 text-amber-100",
};

const toneIcons = {
  success: CheckCircle2,
  info: Info,
  warning: TriangleAlert,
};

export function ToastProvider({ children }: PropsWithChildren) {
  const [items, setItems] = useState<ToastItem[]>([]);

  const pushToast = useCallback((toast: Omit<ToastItem, "id">) => {
    const id = crypto.randomUUID();
    setItems((current) => [...current, { ...toast, id }]);
    window.setTimeout(() => {
      setItems((current) => current.filter((item) => item.id !== id));
    }, 3200);
  }, []);

  const value = useMemo(() => ({ pushToast }), [pushToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 top-4 z-[60] flex w-full max-w-sm flex-col gap-3">
        <AnimatePresence>
          {items.map((item) => {
            const Icon = toneIcons[item.tone];

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: -10, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -6, scale: 0.96 }}
                className={cn(
                  "pointer-events-auto rounded-2xl border px-4 py-3 shadow-soft backdrop-blur-xl",
                  toneStyles[item.tone],
                )}
              >
                <div className="flex items-start gap-3">
                  <Icon className="mt-0.5 h-4 w-4 shrink-0" />
                  <div>
                    <p className="text-sm font-semibold">{item.title}</p>
                    <p className="mt-1 text-xs text-current/90">{item.description}</p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

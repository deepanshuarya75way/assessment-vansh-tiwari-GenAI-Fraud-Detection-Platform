import { AnimatePresence, motion } from "framer-motion";
import { BrowserRouter, Route, Routes, useLocation } from "react-router-dom";
import { PublicLayout } from "@/layouts/PublicLayout";
import { DashboardLayout } from "@/layouts/DashboardLayout";
import { ThemeProvider } from "@/context/ThemeContext";
import { ToastProvider } from "@/context/ToastContext";
import { AnalysisProvider } from "@/context/AnalysisContext";
import { LandingPage } from "@/pages/Landing/LandingPage";
import { WelcomePage } from "@/pages/Welcome/WelcomePage";
import { UploadPage } from "@/pages/Upload/UploadPage";
import { ProcessingPage } from "@/pages/Processing/ProcessingPage";

import { DashboardPage } from "@/pages/Dashboard/DashboardPage";
import { FraudDetailsPage } from "@/pages/Dashboard/FraudDetailsPage";
import { ExplainabilityPage } from "@/pages/Dashboard/ExplainabilityPage";
import { ChatbotPage } from "@/pages/Chatbot/ChatbotPage";
import { ReportsPage } from "@/pages/Reports/ReportsPage";
import { SettingsPage } from "@/pages/Settings/SettingsPage";

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.28, ease: "easeOut" }}
        className="min-h-screen"
      >
        <Routes location={location}>
          <Route element={<PublicLayout />}>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/landing" element={<LandingPage />} />
          </Route>


          <Route element={<DashboardLayout />}>
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/processing" element={<ProcessingPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />

            <Route
              path="/dashboard/fraud-details"
              element={<FraudDetailsPage />}
            />
            <Route
              path="/dashboard/explainability"
              element={<ExplainabilityPage />}
            />
            <Route path="/chatbot" element={<ChatbotPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </motion.div>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AnalysisProvider>
          <BrowserRouter>
            <AnimatedRoutes />
          </BrowserRouter>
        </AnalysisProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

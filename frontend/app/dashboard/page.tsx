"use client";

import { HoverButton } from "@/components/ui/hover-button";

const STREAMLIT_BASE = process.env.NEXT_PUBLIC_STREAMLIT_URL ?? "http://localhost:8501";

const pages = [
  {
    step: "Step 1",
    title: "Data Entry",
    desc: "Record transactions manually or upload a bank screenshot and let AI extract the details automatically.",
    href: `${STREAMLIT_BASE}/Data_Entry`,
    accent: "#1B5E20",
    label: "Go to Data Entry",
  },
  {
    step: "Step 2",
    title: "Transaction Ledger",
    desc: "View, filter, and manage all recorded transactions with live income vs. expense summaries.",
    href: `${STREAMLIT_BASE}/Transaction_Ledger`,
    accent: "#388E3C",
    label: "Go to Ledger",
  },
  {
    step: "Step 3",
    title: "AI Financial Advisor",
    desc: "Get personalized spending analysis, category breakdowns, and a concrete loan-clearing strategy.",
    href: `${STREAMLIT_BASE}/AI_Advisor`,
    accent: "#4CAF50",
    label: "Go to AI Advisor",
  },
  {
    step: "Step 4",
    title: "Loans & Reminders",
    desc: "Track EMIs and credit card due dates with automated upcoming-payment reminders.",
    href: `${STREAMLIT_BASE}/Loans_and_Reminders`,
    accent: "#2E7D32",
    label: "Go to Loans",
  },
  {
    step: "Setup",
    title: "Settings",
    desc: "Configure your Gemini API key, manage family profiles, and connect your Google Sheet.",
    href: `${STREAMLIT_BASE}/Settings`,
    accent: "#66BB6A",
    label: "Go to Settings",
  },
];

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav
        className="sticky top-0 z-50 flex items-center justify-between px-6 py-3 border-b"
        style={{ background: "#1B5E20", borderColor: "#2E7D32" }}
      >
        <span className="text-white font-black text-xl tracking-tight">PIEZA</span>
        <HoverButton href={STREAMLIT_BASE} className="py-2 px-4 text-xs">
          Open Streamlit App
        </HoverButton>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-10">
        {/* Hero */}
        <div
          className="rounded-2xl p-10 mb-8 border"
          style={{
            borderLeft: "4px solid #1B5E20",
            borderColor: "#E8E8E8",
            borderLeftColor: "#1B5E20",
            boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
          }}
        >
          <div className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">
            Personal Finance
          </div>
          <h1 className="text-5xl font-black mb-3" style={{ color: "#1B5E20" }}>
            PIEZA
          </h1>
          <p className="text-gray-500 text-base max-w-lg leading-relaxed mb-6">
            A unified family finance tracker — record every transaction, view real-time
            summaries, and get AI-powered spending advice.
          </p>
          <div className="flex gap-3 flex-wrap items-center">
            <HoverButton href={`${STREAMLIT_BASE}/Data_Entry`}>
              Get Started — Data Entry
            </HoverButton>
            <div className="flex gap-2 flex-wrap">
              {["Google Sheets", "Gemini AI", "Multi-profile"].map((tag) => (
                <span
                  key={tag}
                  className="text-xs font-semibold px-3 py-1 rounded-full"
                  style={{
                    background: "#EBF5EB",
                    color: "#1B5E20",
                    border: "1px solid #A5D6A7",
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Feature cards */}
        <h2 className="text-lg font-bold text-gray-800 mb-4">Where would you like to go?</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {pages.map((p) => (
            <div
              key={p.title}
              className="rounded-xl p-6 flex flex-col border"
              style={{
                borderTopWidth: "3px",
                borderTopColor: p.accent,
                borderColor: "#E8E8E8",
                borderTopStyle: "solid",
                boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
              }}
            >
              <div className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-2">
                {p.step}
              </div>
              <div className="text-base font-bold text-gray-900 mb-2">{p.title}</div>
              <p className="text-sm text-gray-500 leading-relaxed flex-1 mb-4">{p.desc}</p>
              <HoverButton href={p.href} className="self-start text-xs py-2 px-4">
                {p.label}
              </HoverButton>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

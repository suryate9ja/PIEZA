"use client";

import { useId, useRef } from "react";
import { motion } from "framer-motion";

export function PulseBeams() {
  const id = useId();

  const beams = [
    {
      path: "M-380 -189C-380 -189 -312 216 152 343C616 470 684 875 684 875",
      dur: 2,
      delay: 0,
    },
    {
      path: "M-373 -194C-373 -194 -305 211 159 338C623 465 691 870 691 870",
      dur: 2.5,
      delay: 0.4,
    },
    {
      path: "M-100 0C-100 0 -50 200 100 300C250 400 300 600 300 600",
      dur: 3,
      delay: 0.8,
    },
    {
      path: "M200 -50C200 -50 250 150 400 250C550 350 600 600 600 600",
      dur: 2.2,
      delay: 1.2,
    },
    {
      path: "M500 100C500 100 520 300 620 400C720 500 750 700 750 700",
      dur: 2.8,
      delay: 1.6,
    },
  ];

  const connections = [
    { cx: 152, cy: 343 },
    { cx: 159, cy: 338 },
    { cx: 100, cy: 300 },
    { cx: 400, cy: 250 },
    { cx: 620, cy: 400 },
    { cx: 684, cy: 875 },
    { cx: 691, cy: 870 },
    { cx: 300, cy: 600 },
    { cx: 600, cy: 600 },
    { cx: 750, cy: 700 },
  ];

  return (
    <div
      className="relative w-full overflow-hidden flex items-center justify-center"
      style={{ background: "#020c02", height: "100vh" }}
    >
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 858 434"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          {beams.map((beam, i) => (
            <motion.linearGradient
              key={i}
              id={`${id}-grad-${i}`}
              gradientUnits="userSpaceOnUse"
              initial={{ x1: "0%", x2: "0%", y1: "80%", y2: "100%" }}
              animate={{
                x1: ["0%", "20%", "40%", "0%"],
                x2: ["0%", "20%", "40%", "0%"],
                y1: ["80%", "0%", "80%", "80%"],
                y2: ["100%", "20%", "100%", "100%"],
              }}
              transition={{
                duration: beam.dur,
                delay: beam.delay,
                repeat: Infinity,
                repeatDelay: 2,
                ease: "easeInOut",
              }}
            >
              <stop offset="0%" stopColor="#FFD700" stopOpacity="0" />
              <stop offset="30%" stopColor="#FFD700" />
              <stop offset="60%" stopColor="#FFFFFF" />
              <stop offset="100%" stopColor="#22c55e" stopOpacity="0" />
            </motion.linearGradient>
          ))}
        </defs>

        {/* Static path tracks */}
        {beams.map((beam, i) => (
          <path
            key={`track-${i}`}
            d={beam.path}
            stroke="#0d2e0d"
            strokeWidth="1.5"
            fill="none"
          />
        ))}

        {/* Animated gradient paths */}
        {beams.map((beam, i) => (
          <path
            key={`beam-${i}`}
            d={beam.path}
            stroke={`url(#${id}-grad-${i})`}
            strokeWidth="2"
            fill="none"
          />
        ))}

        {/* Connection circles */}
        {connections.map((pt, i) => (
          <circle
            key={i}
            cx={pt.cx}
            cy={pt.cy}
            r="3"
            fill="#0d2e0d"
            stroke="#1a5c1a"
            strokeWidth="1"
          />
        ))}
      </svg>

      {/* Center card */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-0 text-center px-6">
        <div
          className="px-10 py-8 rounded-2xl"
          style={{
            background: "rgba(0,30,0,0.45)",
            border: "1px solid rgba(255,215,0,0.2)",
            boxShadow:
              "0 0 80px rgba(34,197,94,0.12), 0 0 40px rgba(255,215,0,0.08), inset 0 1px 0 rgba(255,215,0,0.12)",
            backdropFilter: "blur(12px)",
          }}
        >
          <h1
            className="text-6xl font-black tracking-tight mb-2"
            style={{
              background: "linear-gradient(135deg, #FFD700 0%, #FFFFFF 50%, #86efac 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            PIEZA
          </h1>
          <p
            className="text-sm max-w-xs leading-relaxed mb-7"
            style={{ color: "rgba(255,255,255,0.55)" }}
          >
            A unified family finance tracker — record every transaction,
            view real-time summaries, and get AI-powered spending advice.
          </p>
          <HoverButtonInline href="/dashboard">Enter App</HoverButtonInline>
        </div>
      </div>
    </div>
  );
}

function HoverButtonInline({
  children,
  href,
}: {
  children: React.ReactNode;
  href: string;
}) {
  const ref = useRef<HTMLButtonElement>(null);

  function spawn(e: React.MouseEvent<HTMLButtonElement>) {
    const btn = ref.current;
    if (!btn) return;
    const r = btn.getBoundingClientRect();
    const x = e.clientX - r.left;
    const y = e.clientY - r.top;
    const el = document.createElement("span");
    el.style.cssText = `
      position:absolute; pointer-events:none; border-radius:9999px;
      width:80px; height:80px; left:${x - 40}px; top:${y - 40}px;
      background:radial-gradient(circle,rgba(255,215,0,0.35) 0%,transparent 70%);
      transform:scale(0); animation:pz-hb-pop 0.6s ease-out forwards;
    `;
    btn.appendChild(el);
    setTimeout(() => el.remove(), 650);
  }

  return (
    <button
      ref={ref}
      onMouseMove={spawn}
      onClick={() => window.location.assign(href)}
      className="relative overflow-hidden px-8 py-3 rounded-full font-semibold text-sm cursor-pointer select-none"
      style={{
        background: "linear-gradient(135deg, #b8860b 0%, #FFD700 50%, #fef08a 100%)",
        border: "1px solid rgba(255,215,0,0.4)",
        boxShadow:
          "inset 0 1px 0 rgba(255,255,255,0.2), 0 4px 24px rgba(255,215,0,0.35)",
        color: "#020c02",
      }}
    >
      <span className="relative z-10 font-bold">{children}</span>
    </button>
  );
}

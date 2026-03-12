"use client";

import { useRef, MouseEvent } from "react";
import { cn } from "@/lib/utils";

interface HoverButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  href?: string;
  className?: string;
}

export function HoverButton({ children, onClick, href, className }: HoverButtonProps) {
  const btnRef = useRef<HTMLButtonElement>(null);

  function spawnCircle(e: MouseEvent<HTMLButtonElement>) {
    const btn = btnRef.current;
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const circle = document.createElement("span");
    circle.style.cssText = `
      position: absolute;
      pointer-events: none;
      border-radius: 9999px;
      width: 80px;
      height: 80px;
      left: ${x - 40}px;
      top: ${y - 40}px;
      background: radial-gradient(circle, rgba(255,255,255,0.35) 0%, transparent 70%);
      transform: scale(0);
      animation: pz-hb-pop 0.6s ease-out forwards;
    `;
    btn.appendChild(circle);
    setTimeout(() => circle.remove(), 650);
  }

  const handleClick = () => {
    if (href) window.location.assign(href);
    onClick?.();
  };

  return (
    <button
      ref={btnRef}
      onMouseMove={spawnCircle}
      onClick={handleClick}
      className={cn(
        "relative overflow-hidden px-6 py-3 rounded-full font-semibold text-sm",
        "bg-[#1B5E20] text-white border border-[#2E7D32]",
        "backdrop-blur-sm shadow-[inset_0_1px_0_rgba(255,255,255,0.15),0_4px_16px_rgba(27,94,32,0.35)]",
        "transition-all duration-200 hover:bg-[#2E7D32] hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_6px_24px_rgba(27,94,32,0.5)]",
        "cursor-pointer select-none",
        className
      )}
    >
      <span className="relative z-10">{children}</span>
    </button>
  );
}

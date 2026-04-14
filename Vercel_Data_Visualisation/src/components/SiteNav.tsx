"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ThemeToggle } from "@/components/ThemeToggle";

const links = [
  { id: "project", href: "/#project", label: "Overview" },
  { id: "data", href: "/#data", label: "Data" },
  { id: "scripts", href: "/#scripts", label: "Scripts" },
  { id: "eda", href: "/#eda", label: "EDA" },
  { id: "hypotheses", href: "/#hypotheses", label: "Hypothesis" },
  { id: "appendix", href: "/#appendix", label: "Appendix" },
];

export function SiteNav() {
  const [activeSection, setActiveSection] = useState("project");

  useEffect(() => {
    const sections = links
      .map((link) => document.getElementById(link.id))
      .filter((section): section is HTMLElement => section !== null);

    const observer = new IntersectionObserver(
      (entries) => {
        const visibleEntry = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (visibleEntry?.target.id) {
          setActiveSection(visibleEntry.target.id);
        }
      },
      { rootMargin: "-18% 0px -62% 0px", threshold: [0.12, 0.3, 0.6] },
    );

    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);

  return (
    <header className="fixed left-0 right-0 top-0 z-50 border-b border-white/10 bg-ink/75 backdrop-blur-xl">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 md:py-5">
        <Link href="/" className="font-display text-xl tracking-wide text-chalk">
          DSA210 Data Story
        </Link>
        <div className="hidden items-center gap-3 md:flex">
          {links.map((link) => {
            const isActive = activeSection === link.id;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setActiveSection(link.id)}
                aria-current={isActive ? "page" : undefined}
                className={`nav-link ${
                  isActive
                    ? "nav-link-active"
                    : "text-parchment hover:border-white/30 hover:bg-white/10 hover:text-chalk"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
          <div className="nav-theme-slot">
            <ThemeToggle />
          </div>
        </div>
      </nav>
    </header>
  );
}

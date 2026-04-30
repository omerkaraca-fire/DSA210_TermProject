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
    let animationFrame = 0;

    function updateActiveSection() {
      const headerHeight = document.querySelector("header")?.getBoundingClientRect().height ?? 0;
      const sectionFocusLine = headerHeight + window.innerHeight * 0.28;
      const pageBottom = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4;

      if (pageBottom) {
        setActiveSection(links[links.length - 1].id);
        return;
      }

      const sections = links
        .map((link) => ({ id: link.id, element: document.getElementById(link.id) }))
        .filter((section): section is { id: string; element: HTMLElement } => section.element !== null);

      const currentSection =
        sections.find(({ element }) => {
          const rect = element.getBoundingClientRect();
          return rect.top <= sectionFocusLine && rect.bottom > sectionFocusLine;
        })?.id ??
        sections
          .filter(({ element }) => element.getBoundingClientRect().top <= sectionFocusLine)
          .at(-1)?.id ??
        links[0].id;

      setActiveSection(currentSection);
    }

    function requestActiveSectionUpdate() {
      window.cancelAnimationFrame(animationFrame);
      animationFrame = window.requestAnimationFrame(updateActiveSection);
    }

    updateActiveSection();
    window.addEventListener("scroll", requestActiveSectionUpdate, { passive: true });
    window.addEventListener("resize", requestActiveSectionUpdate);
    window.addEventListener("hashchange", requestActiveSectionUpdate);
    window.addEventListener("load", requestActiveSectionUpdate);

    return () => {
      window.cancelAnimationFrame(animationFrame);
      window.removeEventListener("scroll", requestActiveSectionUpdate);
      window.removeEventListener("resize", requestActiveSectionUpdate);
      window.removeEventListener("hashchange", requestActiveSectionUpdate);
      window.removeEventListener("load", requestActiveSectionUpdate);
    };
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

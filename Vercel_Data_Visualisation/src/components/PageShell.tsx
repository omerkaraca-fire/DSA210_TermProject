import type { ReactNode } from "react";
import { Reveal } from "@/components/Reveal";

type PageShellProps = {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
};

export function PageShell({ eyebrow, title, description, children }: PageShellProps) {
  return (
    <main className="page-shell">
      <section className="hero-grid pt-32">
        <Reveal className="max-w-4xl">
          <p className="eyebrow">{eyebrow}</p>
          <h1 className="hero-title">{title}</h1>
          <p className="hero-copy">{description}</p>
        </Reveal>
      </section>
      {children}
    </main>
  );
}

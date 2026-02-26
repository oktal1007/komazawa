import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "バステト神AI占い鑑定レポート自動生成",
  description:
    "月花の守猫 バステリア・ルアによる鑑定レポート自動生成システム",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-mystic antialiased">
        <header className="border-b border-[rgba(201,168,76,0.2)] px-6 py-4">
          <div className="mx-auto flex max-w-5xl items-center justify-between">
            <a href="/" className="text-gold-gradient text-xl font-bold">
              月花の守猫 バステリア・ルア
            </a>
            <nav className="flex gap-6 text-sm text-[#e8dcc8]/60">
              <a href="/" className="hover:text-[#c9a84c] transition-colors">
                TOP
              </a>
              <a
                href="/divination"
                className="hover:text-[#c9a84c] transition-colors"
              >
                鑑定作成
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-5xl px-6 py-8">{children}</main>
        <footer className="border-t border-[rgba(201,168,76,0.2)] px-6 py-6 text-center text-xs text-[#e8dcc8]/40">
          <p>月の光と古代の叡智に包まれて — 月花の守猫 バステリア・ルア</p>
        </footer>
      </body>
    </html>
  );
}

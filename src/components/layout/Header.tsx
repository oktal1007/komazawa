import Link from "next/link";
import { siteConfig } from "@/lib/config";

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md">
      <nav className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4">
        <Link href="/" className="text-xl font-bold text-gray-900">
          {siteConfig.title}
        </Link>
        <div className="flex items-center gap-6">
          <Link
            href="/"
            className="text-sm font-medium text-gray-600 hover:text-gray-900"
          >
            ホーム
          </Link>
          <Link
            href="/categories"
            className="text-sm font-medium text-gray-600 hover:text-gray-900"
          >
            カテゴリ
          </Link>
          <Link
            href="/about"
            className="text-sm font-medium text-gray-600 hover:text-gray-900"
          >
            About
          </Link>
        </div>
      </nav>
    </header>
  );
}

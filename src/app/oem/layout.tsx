"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Search,
  MessageSquare,
  TrendingUp,
  Factory,
  Calculator,
} from "lucide-react";

const navItems = [
  { href: "/oem", label: "ダッシュボード", icon: LayoutDashboard },
  { href: "/oem/research", label: "市場リサーチ", icon: Search },
  { href: "/oem/review", label: "口コミ分析", icon: MessageSquare },
  { href: "/oem/trends", label: "成分トレンド", icon: TrendingUp },
  { href: "/oem/factories", label: "OEM工場DB", icon: Factory },
  { href: "/oem/simulator", label: "利益シミュレーター", icon: Calculator },
];

export default function OemLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col fixed h-full">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">OEM Research</h1>
          <p className="text-xs text-gray-500 mt-1">商品開発リサーチツール</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/oem" && pathname.startsWith(item.href));
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-blue-50 text-blue-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                }`}
              >
                <Icon className="w-5 h-5" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-gray-200">
          <p className="text-xs text-gray-400 text-center">
            OEM Research Dashboard v1.0
          </p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 ml-64">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}

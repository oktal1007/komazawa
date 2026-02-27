"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Search,
  MessageSquare,
  TrendingUp,
  Factory,
  Calculator,
  ArrowRight,
  Activity,
  Package,
  DollarSign,
  BarChart3,
} from "lucide-react";
import { getResearchHistory, getIngredientTrends } from "@/lib/oem-api";
import type { MarketResearchItem, IngredientTrend } from "@/lib/oem-api";

const quickActions = [
  {
    href: "/oem/research",
    label: "市場リサーチ",
    desc: "キーワードで市場調査",
    icon: Search,
    color: "bg-blue-500",
  },
  {
    href: "/oem/review",
    label: "口コミ分析",
    desc: "競合レビューをAI分析",
    icon: MessageSquare,
    color: "bg-purple-500",
  },
  {
    href: "/oem/trends",
    label: "成分トレンド",
    desc: "注目成分をチェック",
    icon: TrendingUp,
    color: "bg-green-500",
  },
  {
    href: "/oem/factories",
    label: "OEM工場DB",
    desc: "製造パートナー検索",
    icon: Factory,
    color: "bg-orange-500",
  },
  {
    href: "/oem/simulator",
    label: "利益シミュレーター",
    desc: "収益性を試算",
    icon: Calculator,
    color: "bg-pink-500",
  },
];

export default function OemDashboard() {
  const [recentResearch, setRecentResearch] = useState<MarketResearchItem[]>(
    []
  );
  const [trends, setTrends] = useState<IngredientTrend[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [researchData, trendsData] = await Promise.allSettled([
          getResearchHistory(),
          getIngredientTrends(4),
        ]);
        if (researchData.status === "fulfilled") {
          setRecentResearch(researchData.value.slice(0, 5));
        }
        if (trendsData.status === "fulfilled") {
          setTrends(trendsData.value.slice(0, 5));
        }
      } catch {
        // API not available yet
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">ダッシュボード</h1>
        <p className="text-gray-500 mt-1">
          OEM商品開発のための総合リサーチツール
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          {
            label: "リサーチ件数",
            value: recentResearch.length || "—",
            icon: Activity,
            color: "text-blue-600",
          },
          {
            label: "注目成分",
            value: trends.length ? `${trends.length}件` : "—",
            icon: Package,
            color: "text-green-600",
          },
          {
            label: "登録工場",
            value: "—",
            icon: Factory,
            color: "text-orange-600",
          },
          {
            label: "シミュレーション",
            value: "—",
            icon: DollarSign,
            color: "text-pink-600",
          },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white rounded-xl border border-gray-200 p-5"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className="text-2xl font-bold mt-1">{stat.value}</p>
              </div>
              <stat.icon className={`w-8 h-8 ${stat.color} opacity-50`} />
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          クイックアクセス
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.href}
                href={action.href}
                className="group bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-all hover:border-gray-300"
              >
                <div
                  className={`w-10 h-10 ${action.color} rounded-lg flex items-center justify-center mb-3`}
                >
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                  {action.label}
                </h3>
                <p className="text-sm text-gray-500 mt-1">{action.desc}</p>
                <ArrowRight className="w-4 h-4 text-gray-400 mt-3 group-hover:translate-x-1 transition-transform" />
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Research & Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Research */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              最近のリサーチ
            </h2>
            <Link
              href="/oem/research"
              className="text-sm text-blue-600 hover:underline"
            >
              すべて表示
            </Link>
          </div>
          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-12 bg-gray-100 rounded-lg animate-pulse"
                />
              ))}
            </div>
          ) : recentResearch.length > 0 ? (
            <div className="space-y-3">
              {recentResearch.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {item.title}
                    </p>
                    <p className="text-xs text-gray-500">{item.keyword}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      ¥{item.price?.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">
                      スコア: {item.market_score}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <BarChart3 className="w-10 h-10 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">
                まだリサーチデータがありません
              </p>
              <Link
                href="/oem/research"
                className="text-sm text-blue-600 hover:underline mt-1 inline-block"
              >
                リサーチを開始する
              </Link>
            </div>
          )}
        </div>

        {/* Trend Ingredients */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              注目成分トレンド
            </h2>
            <Link
              href="/oem/trends"
              className="text-sm text-blue-600 hover:underline"
            >
              すべて表示
            </Link>
          </div>
          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-12 bg-gray-100 rounded-lg animate-pulse"
                />
              ))}
            </div>
          ) : trends.length > 0 ? (
            <div className="space-y-3">
              {trends.map((trend, idx) => (
                <div
                  key={trend.id}
                  className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 bg-green-100 text-green-700 rounded-full text-xs font-bold flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <p className="text-sm font-medium text-gray-900">
                      {trend.ingredient_name}
                    </p>
                  </div>
                  <div className="text-right">
                    <p
                      className={`text-sm font-medium ${trend.growth_rate > 0 ? "text-green-600" : "text-red-600"}`}
                    >
                      {trend.growth_rate > 0 ? "+" : ""}
                      {(trend.growth_rate * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500">
                      {trend.mention_count}件
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <TrendingUp className="w-10 h-10 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">
                トレンドデータがありません
              </p>
              <Link
                href="/oem/trends"
                className="text-sm text-blue-600 hover:underline mt-1 inline-block"
              >
                トレンドを確認する
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

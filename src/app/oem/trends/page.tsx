"use client";

import { useState, useEffect } from "react";
import {
  TrendingUp,
  Loader2,
  RefreshCw,
  AlertTriangle,
  Sparkles,
} from "lucide-react";
import { getIngredientTrends, getTrendReport } from "@/lib/oem-api";
import type { IngredientTrend, TrendReport } from "@/lib/oem-api";
import LineChart from "@/components/oem/charts/LineChart";
import BarChart from "@/components/oem/charts/BarChart";

export default function TrendsPage() {
  const [trends, setTrends] = useState<IngredientTrend[]>([]);
  const [report, setReport] = useState<TrendReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [weeks, setWeeks] = useState(12);

  useEffect(() => {
    loadData();
  }, [weeks]);

  async function loadData() {
    setLoading(true);
    try {
      const [trendsData, reportData] = await Promise.allSettled([
        getIngredientTrends(weeks),
        getTrendReport(),
      ]);
      if (trendsData.status === "fulfilled") setTrends(trendsData.value);
      if (reportData.status === "fulfilled") setReport(reportData.value);
    } catch {
      // API not available
    } finally {
      setLoading(false);
    }
  }

  // Group trends by ingredient for chart
  const ingredientNames = [...new Set(trends.map((t) => t.ingredient_name))];
  const topIngredients = ingredientNames.slice(0, 10);

  const rankingData = topIngredients.map((name) => {
    const latestEntry = trends
      .filter((t) => t.ingredient_name === name)
      .sort(
        (a, b) =>
          new Date(b.week_date).getTime() - new Date(a.week_date).getTime()
      )[0];
    return {
      name,
      mention_count: latestEntry?.mention_count || 0,
      growth_rate: latestEntry?.growth_rate || 0,
      market_size: latestEntry?.market_size || 0,
    };
  });

  // Growth chart data by week
  const weekDates = [...new Set(trends.map((t) => t.week_date))].sort();
  const growthChartData = weekDates.map((date) => {
    const entry: Record<string, string | number> = { date };
    topIngredients.slice(0, 5).forEach((name) => {
      const t = trends.find(
        (tr) => tr.ingredient_name === name && tr.week_date === date
      );
      entry[name] = t?.mention_count || 0;
    });
    return entry;
  });

  const lineColors = [
    "#3B82F6",
    "#10B981",
    "#F59E0B",
    "#EF4444",
    "#8B5CF6",
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            成分トレンド
          </h1>
          <p className="text-gray-500 mt-1">
            注目成分のランキングとトレンド推移を確認できます
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={weeks}
            onChange={(e) => setWeeks(Number(e.target.value))}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            <option value={4}>過去4週間</option>
            <option value={12}>過去12週間</option>
            <option value={24}>過去24週間</option>
          </select>
          <button
            onClick={loadData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50"
          >
            <RefreshCw
              className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
            />
            更新
          </button>
        </div>
      </div>

      {loading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Loader2 className="w-10 h-10 animate-spin text-green-500 mx-auto mb-4" />
          <p className="text-gray-600">トレンドデータを読み込み中...</p>
        </div>
      ) : (
        <>
          {/* Ingredient Ranking */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              注目成分ランキング
            </h2>
            {rankingData.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-gray-600">
                        順位
                      </th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600">
                        成分名
                      </th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600">
                        出現数
                      </th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600">
                        成長率
                      </th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600">
                        市場規模（推定）
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {rankingData
                      .sort((a, b) => b.mention_count - a.mention_count)
                      .map((item, idx) => (
                        <tr key={item.name} className="hover:bg-gray-50">
                          <td className="px-4 py-3">
                            <span
                              className={`w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center ${
                                idx < 3
                                  ? "bg-yellow-100 text-yellow-700"
                                  : "bg-gray-100 text-gray-600"
                              }`}
                            >
                              {idx + 1}
                            </span>
                          </td>
                          <td className="px-4 py-3 font-medium text-gray-900">
                            {item.name}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {item.mention_count.toLocaleString()}件
                          </td>
                          <td className="px-4 py-3 text-right">
                            <span
                              className={`inline-flex items-center gap-1 ${
                                item.growth_rate > 0
                                  ? "text-green-600"
                                  : item.growth_rate < 0
                                    ? "text-red-600"
                                    : "text-gray-600"
                              }`}
                            >
                              {item.growth_rate > 0 ? (
                                <TrendingUp className="w-3 h-3" />
                              ) : item.growth_rate < 0 ? (
                                <AlertTriangle className="w-3 h-3" />
                              ) : null}
                              {item.growth_rate > 0 ? "+" : ""}
                              {(item.growth_rate * 100).toFixed(1)}%
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right text-gray-600">
                            ¥{(item.market_size / 100000000).toFixed(1)}億
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center py-8">
                トレンドデータがありません
              </p>
            )}
          </div>

          {/* Trend Chart */}
          {growthChartData.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                成分トレンド推移（TOP5）
              </h2>
              <LineChart
                data={growthChartData}
                lines={topIngredients.slice(0, 5).map((name, i) => ({
                  dataKey: name,
                  color: lineColors[i],
                  name,
                }))}
                xDataKey="date"
                height={350}
              />
            </div>
          )}

          {/* Bar Chart - Mention Count */}
          {rankingData.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                成分別出現数
              </h2>
              <BarChart
                data={rankingData
                  .sort((a, b) => b.mention_count - a.mention_count)
                  .slice(0, 10)}
                bars={[
                  {
                    dataKey: "mention_count",
                    color: "#10B981",
                    name: "出現数",
                  },
                ]}
                xDataKey="name"
                height={300}
              />
            </div>
          )}

          {/* AI Report */}
          {report && (
            <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl border border-green-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-green-500" />
                Claude AI 週次トレンドレポート
              </h2>
              <p className="text-xs text-gray-500 mb-4">
                生成日: {new Date(report.generated_at).toLocaleString("ja-JP")}
              </p>

              {report.top_ingredients.length > 0 && (
                <div className="mb-4">
                  <h3 className="font-medium text-gray-800 mb-2">
                    今注目すべき成分
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {report.top_ingredients.map((ing) => (
                      <span
                        key={ing}
                        className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium"
                      >
                        {ing}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
                {report.report}
              </div>

              {report.predictions.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-medium text-gray-800 mb-2">
                    市場予測
                  </h3>
                  <ul className="space-y-2">
                    {report.predictions.map((pred, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm text-gray-700"
                      >
                        <span className="w-5 h-5 bg-blue-100 text-blue-600 rounded-full text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                          {i + 1}
                        </span>
                        {pred}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

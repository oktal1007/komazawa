"use client";

import { useState } from "react";
import { Search, Loader2, MessageSquare, Lightbulb, Target, ThumbsDown, ThumbsUp } from "lucide-react";
import { analyzeReviews } from "@/lib/oem-api";
import type { ReviewAnalysisResult } from "@/lib/oem-api";
import PieChart from "@/components/oem/charts/PieChart";

export default function ReviewPage() {
  const [asin, setAsin] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReviewAnalysisResult | null>(null);
  const [error, setError] = useState("");

  async function handleAnalyze(e: React.FormEvent) {
    e.preventDefault();
    if (!asin.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await analyzeReviews(asin.trim());
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "分析中にエラーが発生しました"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">口コミ分析</h1>
        <p className="text-gray-500 mt-1">
          競合商品のレビューをAIで分析し、差別化ポイントを発見します
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleAnalyze} className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={asin}
            onChange={(e) => setAsin(e.target.value)}
            placeholder="ASINを入力（例：B0XXXXXXXXX）"
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !asin.trim()}
          className="px-6 py-3 bg-purple-600 text-white rounded-lg font-medium text-sm hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <MessageSquare className="w-4 h-4" />
          )}
          AI分析開始
        </button>
      </form>

      {loading && (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Loader2 className="w-10 h-10 animate-spin text-purple-500 mx-auto mb-4" />
          <p className="text-gray-600 font-medium">レビューを分析中...</p>
          <p className="text-sm text-gray-400 mt-1">
            Claude AIがレビューを読み込んでいます
          </p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          {/* Header */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h2 className="font-semibold text-gray-900">
                  分析結果: {result.asin}
                </h2>
                <p className="text-xs text-gray-500">
                  {new Date(result.created_at).toLocaleString("ja-JP")}
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Negative Categories Pie Chart */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <ThumbsDown className="w-4 h-4 text-red-500" />
                ネガティブレビュー分類
              </h3>
              {result.negative_categories.length > 0 ? (
                <PieChart
                  data={result.negative_categories.map((c) => ({
                    name: c.name,
                    value: c.count,
                  }))}
                  height={300}
                />
              ) : (
                <p className="text-sm text-gray-500 text-center py-8">
                  データなし
                </p>
              )}
            </div>

            {/* Strengths & Weaknesses */}
            <div className="space-y-4">
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <ThumbsUp className="w-4 h-4 text-green-500" />
                  競合の強み
                </h3>
                <ul className="space-y-2">
                  {result.strengths.map((s, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-sm text-gray-700"
                    >
                      <span className="w-5 h-5 bg-green-100 text-green-600 rounded-full text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      {s}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <ThumbsDown className="w-4 h-4 text-red-500" />
                  競合の弱み
                </h3>
                <ul className="space-y-2">
                  {result.weaknesses.map((w, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-sm text-gray-700"
                    >
                      <span className="w-5 h-5 bg-red-100 text-red-600 rounded-full text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Gap Analysis */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Target className="w-4 h-4 text-blue-500" />
              ギャップ分析（満たされていないニーズ）
            </h3>
            <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
              {result.gap_analysis}
            </div>
          </div>

          {/* Differentiation Points */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-yellow-500" />
              差別化ポイント（「ここを改善すれば勝てる」）
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {result.differentiation_points.map((point, i) => (
                <div
                  key={i}
                  className="bg-yellow-50 border border-yellow-200 rounded-lg p-4"
                >
                  <div className="flex items-start gap-2">
                    <Lightbulb className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-gray-700">{point}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Report */}
          <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border border-purple-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-purple-500" />
              Claude AI 勝てるポイントレポート
            </h3>
            <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
              {result.winning_report}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

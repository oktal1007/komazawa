"use client";

import { useState } from "react";
import { Search, Loader2, ExternalLink, ChevronDown, X } from "lucide-react";
import {
  searchMarket,
  getProductDetails,
} from "@/lib/oem-api";
import type {
  MarketSearchResult,
  MarketResearchItem,
  ProductDetails,
} from "@/lib/oem-api";
import ScoreGauge from "@/components/oem/charts/ScoreGauge";
import BarChart from "@/components/oem/charts/BarChart";
import LineChart from "@/components/oem/charts/LineChart";

export default function ResearchPage() {
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MarketSearchResult | null>(null);
  const [selectedProduct, setSelectedProduct] =
    useState<ProductDetails | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!keyword.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await searchMarket(keyword.trim());
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "検索中にエラーが発生しました"
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleProductClick(asin: string) {
    setDetailLoading(true);
    try {
      const data = await getProductDetails(asin);
      setSelectedProduct(data);
    } catch {
      // ignore
    } finally {
      setDetailLoading(false);
    }
  }

  const priceDistribution = result
    ? (() => {
        const ranges = [
          { range: "~1000円", min: 0, max: 1000 },
          { range: "1001~2000円", min: 1001, max: 2000 },
          { range: "2001~3000円", min: 2001, max: 3000 },
          { range: "3001~5000円", min: 3001, max: 5000 },
          { range: "5001円~", min: 5001, max: Infinity },
        ];
        return ranges.map((r) => ({
          range: r.range,
          count: result.products.filter(
            (p) => p.price >= r.min && p.price <= r.max
          ).length,
        }));
      })()
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Amazon市場リサーチ
        </h1>
        <p className="text-gray-500 mt-1">
          キーワードで市場調査し、参入可能性を評価します
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="調査キーワードを入力（例：マグネシウム サプリ）"
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !keyword.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          調査開始
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <>
          {/* Market Score */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              市場参入スコア
            </h2>
            <div className="flex items-center justify-center gap-8 flex-wrap">
              <ScoreGauge
                score={result.market_score.total}
                label="総合スコア"
              />
              <ScoreGauge
                score={result.market_score.market_size}
                label="市場規模"
              />
              <ScoreGauge
                score={result.market_score.competition}
                label="競合強度"
              />
              <ScoreGauge
                score={result.market_score.price_range}
                label="価格帯"
              />
              <ScoreGauge
                score={result.market_score.trend}
                label="トレンド"
              />
              <ScoreGauge
                score={result.market_score.new_entrant}
                label="新規参入"
              />
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              {
                label: "商品数",
                value: `${result.summary.total_products}件`,
              },
              {
                label: "平均価格",
                value: `¥${result.summary.avg_price.toLocaleString()}`,
              },
              {
                label: "平均評価",
                value: `★${result.summary.avg_rating.toFixed(1)}`,
              },
              {
                label: "月間総売上",
                value: `¥${(result.summary.total_monthly_revenue / 10000).toFixed(0)}万`,
              },
              {
                label: "中央値価格",
                value: `¥${result.summary.median_price.toLocaleString()}`,
              },
              {
                label: "最安値",
                value: `¥${result.summary.min_price.toLocaleString()}`,
              },
              {
                label: "FBA比率",
                value: `${(result.summary.fba_ratio * 100).toFixed(0)}%`,
              },
              {
                label: "新規参入比率",
                value: `${(result.summary.new_entrant_ratio * 100).toFixed(0)}%`,
              },
            ].map((stat) => (
              <div
                key={stat.label}
                className="bg-white rounded-lg border border-gray-200 p-4"
              >
                <p className="text-xs text-gray-500">{stat.label}</p>
                <p className="text-lg font-bold mt-1">{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Price Distribution Chart */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              価格帯分布
            </h2>
            <BarChart
              data={priceDistribution}
              bars={[
                { dataKey: "count", color: "#3B82F6", name: "商品数" },
              ]}
              xDataKey="range"
              height={250}
            />
          </div>

          {/* Products Table */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                売れ筋商品一覧（TOP{result.products.length}）
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">
                      #
                    </th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">
                      商品名
                    </th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">
                      ブランド
                    </th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">
                      価格
                    </th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">
                      レビュー
                    </th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">
                      評価
                    </th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">
                      月間販売数
                    </th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">
                      月間売上
                    </th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600">
                      詳細
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {result.products.map(
                    (product: MarketResearchItem, idx: number) => (
                      <tr key={product.asin} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-gray-500">{idx + 1}</td>
                        <td className="px-4 py-3">
                          <p className="font-medium text-gray-900 truncate max-w-xs">
                            {product.title}
                          </p>
                          <p className="text-xs text-gray-400">
                            {product.asin}
                          </p>
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {product.brand}
                        </td>
                        <td className="px-4 py-3 text-right font-medium">
                          ¥{product.price.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {product.review_count.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-right">
                          ★{product.rating.toFixed(1)}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {product.monthly_sales.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-right">
                          ¥{product.monthly_revenue.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <button
                            onClick={() => handleProductClick(product.asin)}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <ChevronDown className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Product Detail Drawer */}
      {selectedProduct && (
        <div className="fixed inset-0 bg-black/30 z-50 flex justify-end">
          <div className="w-full max-w-2xl bg-white h-full overflow-y-auto shadow-xl">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">商品詳細分析</h3>
              <button
                onClick={() => setSelectedProduct(null)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            {detailLoading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
              </div>
            ) : (
              <div className="p-6 space-y-6">
                <div>
                  <h4 className="text-lg font-semibold">
                    {selectedProduct.title}
                  </h4>
                  <p className="text-sm text-gray-500 mt-1">
                    {selectedProduct.brand} | ASIN: {selectedProduct.asin}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500">現在価格</p>
                    <p className="text-xl font-bold">
                      ¥{selectedProduct.price.toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500">月間販売数</p>
                    <p className="text-xl font-bold">
                      {selectedProduct.monthly_sales.toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500">FBA手数料</p>
                    <p className="text-xl font-bold">
                      ¥{selectedProduct.fba_fee.toLocaleString()}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500">Buy Box獲得率</p>
                    <p className="text-xl font-bold">
                      {(selectedProduct.buy_box_rate * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>

                {/* Price History */}
                {selectedProduct.price_history.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-3">価格推移</h5>
                    <LineChart
                      data={selectedProduct.price_history}
                      lines={[
                        {
                          dataKey: "price",
                          color: "#3B82F6",
                          name: "価格",
                        },
                      ]}
                      xDataKey="date"
                      height={200}
                      yAxisFormatter={(v) => `¥${v.toLocaleString()}`}
                    />
                  </div>
                )}

                {/* Rank History */}
                {selectedProduct.rank_history.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-3">ランキング推移</h5>
                    <LineChart
                      data={selectedProduct.rank_history}
                      lines={[
                        {
                          dataKey: "rank",
                          color: "#10B981",
                          name: "ランキング",
                        },
                      ]}
                      xDataKey="date"
                      height={200}
                    />
                  </div>
                )}

                <div className="flex gap-3">
                  <a
                    href={`https://www.amazon.co.jp/dp/${selectedProduct.asin}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg text-sm hover:bg-orange-600"
                  >
                    <ExternalLink className="w-4 h-4" />
                    Amazonで見る
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import {
  Search,
  Loader2,
  Factory,
  Star,
  ExternalLink,
  X,
  Check,
  Filter,
  LayoutGrid,
  Table,
  MessageSquare,
} from "lucide-react";
import {
  getFactories,
  toggleFactoryFavorite,
  updateFactoryMemo,
} from "@/lib/oem-api";
import type { FactoryItem, FactoryFilters } from "@/lib/oem-api";

const CATEGORIES = [
  "サプリメント",
  "入浴剤",
  "スキンケア",
  "化粧品",
];
const PREFECTURES = [
  "東京都",
  "大阪府",
  "愛知県",
  "静岡県",
  "富山県",
  "新潟県",
  "群馬県",
  "埼玉県",
  "千葉県",
  "神奈川県",
  "兵庫県",
  "福岡県",
  "北海道",
];
const CERTIFICATIONS = ["GMP", "ISO9001", "ISO22000", "HACCP", "有機JAS"];

export default function FactoriesPage() {
  const [factories, setFactories] = useState<FactoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<FactoryFilters>({});
  const [keyword, setKeyword] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [compareIds, setCompareIds] = useState<number[]>([]);
  const [showCompare, setShowCompare] = useState(false);
  const [memoEditId, setMemoEditId] = useState<number | null>(null);
  const [memoText, setMemoText] = useState("");

  useEffect(() => {
    loadFactories();
  }, [filters]);

  async function loadFactories() {
    setLoading(true);
    try {
      const data = await getFactories({ ...filters, keyword: keyword || undefined });
      setFactories(data);
    } catch {
      // API not available
    } finally {
      setLoading(false);
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setFilters((prev) => ({ ...prev, keyword }));
  }

  async function handleToggleFavorite(id: number) {
    try {
      const updated = await toggleFactoryFavorite(id);
      setFactories((prev) =>
        prev.map((f) => (f.id === updated.id ? updated : f))
      );
    } catch {
      // ignore
    }
  }

  async function handleSaveMemo(id: number) {
    try {
      const updated = await updateFactoryMemo(id, memoText);
      setFactories((prev) =>
        prev.map((f) => (f.id === updated.id ? updated : f))
      );
      setMemoEditId(null);
    } catch {
      // ignore
    }
  }

  function toggleCompare(id: number) {
    setCompareIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  const compareFactories = factories.filter((f) =>
    compareIds.includes(f.id)
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">OEM工場データベース</h1>
          <p className="text-gray-500 mt-1">
            国内OEM工場を検索・比較できます
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode("grid")}
            className={`p-2 rounded-lg ${viewMode === "grid" ? "bg-blue-100 text-blue-700" : "text-gray-400 hover:bg-gray-100"}`}
          >
            <LayoutGrid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode("table")}
            className={`p-2 rounded-lg ${viewMode === "table" ? "bg-blue-100 text-blue-700" : "text-gray-400 hover:bg-gray-100"}`}
          >
            <Table className="w-4 h-4" />
          </button>
          {compareIds.length >= 2 && (
            <button
              onClick={() => setShowCompare(true)}
              className="ml-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
            >
              比較する（{compareIds.length}件）
            </button>
          )}
        </div>
      </div>

      {/* Search & Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <form onSubmit={handleSearch} className="flex gap-3 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="キーワードで検索（成分名、特徴など）"
              className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 flex items-center gap-2"
          >
            <Search className="w-4 h-4" />
            検索
          </button>
        </form>
        <div className="flex flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-500">絞り込み:</span>
          </div>
          <select
            value={filters.category || ""}
            onChange={(e) =>
              setFilters((prev) => ({
                ...prev,
                category: e.target.value || undefined,
              }))
            }
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="">カテゴリ</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <select
            value={filters.prefecture || ""}
            onChange={(e) =>
              setFilters((prev) => ({
                ...prev,
                prefecture: e.target.value || undefined,
              }))
            }
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="">都道府県</option>
            {PREFECTURES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <select
            value={filters.certification || ""}
            onChange={(e) =>
              setFilters((prev) => ({
                ...prev,
                certification: e.target.value || undefined,
              }))
            }
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="">認証</option>
            {CERTIFICATIONS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={filters.favorite_only || false}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  favorite_only: e.target.checked || undefined,
                }))
              }
              className="rounded"
            />
            お気に入りのみ
          </label>
          {Object.values(filters).some(Boolean) && (
            <button
              onClick={() => {
                setFilters({});
                setKeyword("");
              }}
              className="text-sm text-red-500 hover:underline"
            >
              クリア
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Loader2 className="w-10 h-10 animate-spin text-orange-500 mx-auto mb-4" />
          <p className="text-gray-600">工場データを読み込み中...</p>
        </div>
      ) : factories.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Factory className="w-10 h-10 text-gray-300 mx-auto mb-2" />
          <p className="text-gray-500">工場データがありません</p>
        </div>
      ) : viewMode === "grid" ? (
        /* Grid View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {factories.map((factory) => (
            <div
              key={factory.id}
              className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {factory.name}
                  </h3>
                  <p className="text-xs text-gray-500">{factory.prefecture}</p>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => toggleCompare(factory.id)}
                    className={`p-1.5 rounded ${compareIds.includes(factory.id) ? "bg-blue-100 text-blue-600" : "text-gray-400 hover:bg-gray-100"}`}
                    title="比較に追加"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleToggleFavorite(factory.id)}
                    className={`p-1.5 rounded ${factory.is_favorite ? "text-yellow-500" : "text-gray-400 hover:bg-gray-100"}`}
                  >
                    <Star
                      className="w-4 h-4"
                      fill={factory.is_favorite ? "currentColor" : "none"}
                    />
                  </button>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex flex-wrap gap-1">
                  {factory.categories.split(",").map((cat) => (
                    <span
                      key={cat}
                      className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs"
                    >
                      {cat.trim()}
                    </span>
                  ))}
                </div>
                <div className="flex flex-wrap gap-1">
                  {factory.dosage_forms.split(",").map((form) => (
                    <span
                      key={form}
                      className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                    >
                      {form.trim()}
                    </span>
                  ))}
                </div>
                <p className="text-gray-600">
                  最小ロット: {factory.min_lot.toLocaleString()}個
                </p>
                {factory.certifications && (
                  <div className="flex flex-wrap gap-1">
                    {factory.certifications.split(",").map((cert) => (
                      <span
                        key={cert}
                        className="px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs"
                      >
                        {cert.trim()}
                      </span>
                    ))}
                  </div>
                )}
                <p className="text-gray-500 text-xs line-clamp-2">
                  {factory.features}
                </p>
              </div>

              <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {factory.url && (
                    <a
                      href={factory.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-xs flex items-center gap-1"
                    >
                      <ExternalLink className="w-3 h-3" />
                      公式サイト
                    </a>
                  )}
                </div>
                <button
                  onClick={() => {
                    setMemoEditId(factory.id);
                    setMemoText(factory.memo || "");
                  }}
                  className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1"
                >
                  <MessageSquare className="w-3 h-3" />
                  メモ
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Table View */
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="w-10 px-4 py-3"></th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">工場名</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">所在地</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">カテゴリ</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">剤形</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-600">最小ロット</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">認証</th>
                  <th className="text-center px-4 py-3 font-medium text-gray-600">お気に入り</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {factories.map((factory) => (
                  <tr key={factory.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <input
                        type="checkbox"
                        checked={compareIds.includes(factory.id)}
                        onChange={() => toggleCompare(factory.id)}
                        className="rounded"
                      />
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {factory.name}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{factory.prefecture}</td>
                    <td className="px-4 py-3">{factory.categories}</td>
                    <td className="px-4 py-3">{factory.dosage_forms}</td>
                    <td className="px-4 py-3 text-right">{factory.min_lot.toLocaleString()}</td>
                    <td className="px-4 py-3">{factory.certifications}</td>
                    <td className="px-4 py-3 text-center">
                      <button onClick={() => handleToggleFavorite(factory.id)}>
                        <Star
                          className={`w-4 h-4 ${factory.is_favorite ? "text-yellow-500" : "text-gray-300"}`}
                          fill={factory.is_favorite ? "currentColor" : "none"}
                        />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Memo Edit Modal */}
      {memoEditId !== null && (
        <div className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">メモ編集</h3>
              <button
                onClick={() => setMemoEditId(null)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <textarea
              value={memoText}
              onChange={(e) => setMemoText(e.target.value)}
              className="w-full h-32 border border-gray-300 rounded-lg p-3 text-sm resize-none focus:ring-2 focus:ring-blue-500"
              placeholder="工場についてのメモを入力..."
            />
            <div className="flex justify-end gap-2 mt-4">
              <button
                onClick={() => setMemoEditId(null)}
                className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                キャンセル
              </button>
              <button
                onClick={() => handleSaveMemo(memoEditId)}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Compare Modal */}
      {showCompare && compareFactories.length >= 2 && (
        <div className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-8">
          <div className="bg-white rounded-xl w-full max-w-5xl max-h-[80vh] overflow-auto shadow-xl">
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">工場比較</h3>
              <button
                onClick={() => setShowCompare(false)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="text-left px-4 py-2 bg-gray-50 font-medium text-gray-600 min-w-[120px]">
                      項目
                    </th>
                    {compareFactories.map((f) => (
                      <th
                        key={f.id}
                        className="text-left px-4 py-2 bg-gray-50 font-medium text-gray-900 min-w-[200px]"
                      >
                        {f.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {[
                    { label: "所在地", key: "prefecture" },
                    { label: "カテゴリ", key: "categories" },
                    { label: "剤形", key: "dosage_forms" },
                    { label: "最小ロット", key: "min_lot" },
                    { label: "認証", key: "certifications" },
                    { label: "特徴", key: "features" },
                  ].map((row) => (
                    <tr key={row.key}>
                      <td className="px-4 py-3 font-medium text-gray-600 bg-gray-50">
                        {row.label}
                      </td>
                      {compareFactories.map((f) => (
                        <td key={f.id} className="px-4 py-3 text-gray-700">
                          {row.key === "min_lot"
                            ? (f[row.key as keyof FactoryItem] as number).toLocaleString() + "個"
                            : String(f[row.key as keyof FactoryItem] || "—")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import {
  Calculator,
  Loader2,
  Save,
  Trash2,
  TrendingUp,
  TrendingDown,
  Minus,
  DollarSign,
} from "lucide-react";
import {
  calculateProfit,
  saveSimulation,
  getSimulationHistory,
  deleteSimulation,
} from "@/lib/oem-api";
import type {
  ProfitInput,
  ProfitResult,
  SimulationHistoryItem,
} from "@/lib/oem-api";
import BarChart from "@/components/oem/charts/BarChart";

const defaultInput: ProfitInput = {
  product_name: "",
  selling_price: 2980,
  manufacturing_cost: 500,
  packaging_cost: 150,
  fba_fee: 580,
  ad_rate: 15,
  target_sales: 300,
};

export default function SimulatorPage() {
  const [input, setInput] = useState<ProfitInput>(defaultInput);
  const [result, setResult] = useState<ProfitResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [history, setHistory] = useState<SimulationHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    setHistoryLoading(true);
    try {
      const data = await getSimulationHistory();
      setHistory(data);
    } catch {
      // API not available
    } finally {
      setHistoryLoading(false);
    }
  }

  async function handleCalculate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await calculateProfit(input);
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "計算中にエラーが発生しました"
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    if (!result) return;
    setSaving(true);
    try {
      await saveSimulation({ ...input, ...result });
      await loadHistory();
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteSimulation(id);
      setHistory((prev) => prev.filter((h) => h.id !== id));
    } catch {
      // ignore
    }
  }

  function updateInput(field: keyof ProfitInput, value: string | number) {
    setInput((prev) => ({ ...prev, [field]: value }));
  }

  const scenarioChartData = result
    ? [
        {
          name: "楽観",
          monthly_profit: result.scenarios.optimistic.monthly_profit,
          annual_profit: result.scenarios.optimistic.annual_profit,
        },
        {
          name: "中立",
          monthly_profit: result.scenarios.neutral.monthly_profit,
          annual_profit: result.scenarios.neutral.annual_profit,
        },
        {
          name: "悲観",
          monthly_profit: result.scenarios.pessimistic.monthly_profit,
          annual_profit: result.scenarios.pessimistic.annual_profit,
        },
      ]
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          利益シミュレーター
        </h1>
        <p className="text-gray-500 mt-1">
          OEM商品の収益性を試算し、3シナリオで比較できます
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Form */}
        <div className="lg:col-span-1">
          <form
            onSubmit={handleCalculate}
            className="bg-white rounded-xl border border-gray-200 p-6 space-y-4"
          >
            <h2 className="font-semibold text-gray-900">入力項目</h2>

            <div>
              <label className="block text-sm text-gray-600 mb-1">
                商品名
              </label>
              <input
                type="text"
                value={input.product_name}
                onChange={(e) => updateInput("product_name", e.target.value)}
                placeholder="例：マグネシウムサプリ 90粒"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">
                想定販売価格（円）
              </label>
              <input
                type="number"
                value={input.selling_price}
                onChange={(e) =>
                  updateInput("selling_price", Number(e.target.value))
                }
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">
                OEM製造原価（円/個）
              </label>
              <input
                type="number"
                value={input.manufacturing_cost}
                onChange={(e) =>
                  updateInput("manufacturing_cost", Number(e.target.value))
                }
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">
                梱包・副資材費（円/個）
              </label>
              <input
                type="number"
                value={input.packaging_cost}
                onChange={(e) =>
                  updateInput("packaging_cost", Number(e.target.value))
                }
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">
                FBA手数料（円/個）
              </label>
              <input
                type="number"
                value={input.fba_fee}
                onChange={(e) =>
                  updateInput("fba_fee", Number(e.target.value))
                }
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">
                広告費率（%）
              </label>
              <input
                type="number"
                value={input.ad_rate}
                onChange={(e) =>
                  updateInput("ad_rate", Number(e.target.value))
                }
                step="0.1"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">
                目標月間販売数
              </label>
              <input
                type="number"
                value={input.target_sales}
                onChange={(e) =>
                  updateInput("target_sales", Number(e.target.value))
                }
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-pink-600 text-white rounded-lg font-medium text-sm hover:bg-pink-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Calculator className="w-4 h-4" />
              )}
              利益を計算する
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          {result && (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <p className="text-xs text-gray-500">1個あたり利益</p>
                  <p className="text-2xl font-bold text-green-600">
                    ¥{result.profit_per_unit.toLocaleString()}
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <p className="text-xs text-gray-500">利益率</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {(result.profit_margin * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <p className="text-xs text-gray-500">月間利益</p>
                  <p className="text-2xl font-bold">
                    ¥{result.monthly_profit.toLocaleString()}
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <p className="text-xs text-gray-500">年間利益</p>
                  <p className="text-2xl font-bold">
                    ¥{result.annual_profit.toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <p className="text-xs text-gray-500">損益分岐点</p>
                  <p className="text-xl font-bold">
                    {result.breakeven_units.toLocaleString()}個/月
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <p className="text-xs text-gray-500">ROI</p>
                  <p className="text-xl font-bold">
                    {(result.roi * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <p className="text-xs text-gray-500">投資回収期間</p>
                  <p className="text-xl font-bold">
                    {result.payback_months.toFixed(1)}ヶ月
                  </p>
                </div>
              </div>

              {/* Scenario Comparison */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-900 mb-4">
                  3シナリオ比較
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left px-4 py-3 font-medium text-gray-600">
                          シナリオ
                        </th>
                        <th className="text-right px-4 py-3 font-medium text-gray-600">
                          月間販売数
                        </th>
                        <th className="text-right px-4 py-3 font-medium text-gray-600">
                          月間利益
                        </th>
                        <th className="text-right px-4 py-3 font-medium text-gray-600">
                          年間利益
                        </th>
                        <th className="text-right px-4 py-3 font-medium text-gray-600">
                          ROI
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {[
                        {
                          label: "楽観",
                          data: result.scenarios.optimistic,
                          icon: TrendingUp,
                          color: "text-green-600",
                        },
                        {
                          label: "中立",
                          data: result.scenarios.neutral,
                          icon: Minus,
                          color: "text-blue-600",
                        },
                        {
                          label: "悲観",
                          data: result.scenarios.pessimistic,
                          icon: TrendingDown,
                          color: "text-red-600",
                        },
                      ].map((scenario) => (
                        <tr key={scenario.label}>
                          <td className="px-4 py-3">
                            <span
                              className={`flex items-center gap-2 font-medium ${scenario.color}`}
                            >
                              <scenario.icon className="w-4 h-4" />
                              {scenario.label}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            {scenario.data.target_sales.toLocaleString()}個
                          </td>
                          <td className="px-4 py-3 text-right font-medium">
                            ¥
                            {scenario.data.monthly_profit.toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-right">
                            ¥{scenario.data.annual_profit.toLocaleString()}
                          </td>
                          <td className="px-4 py-3 text-right">
                            {(scenario.data.roi * 100).toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Scenario Chart */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-900 mb-4">
                  シナリオ別利益比較
                </h3>
                <BarChart
                  data={scenarioChartData}
                  bars={[
                    {
                      dataKey: "monthly_profit",
                      color: "#3B82F6",
                      name: "月間利益",
                    },
                    {
                      dataKey: "annual_profit",
                      color: "#10B981",
                      name: "年間利益",
                    },
                  ]}
                  xDataKey="name"
                  height={300}
                />
              </div>

              {/* Save Button */}
              <div className="flex justify-end">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium text-sm hover:bg-blue-700 disabled:opacity-50"
                >
                  {saving ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4" />
                  )}
                  シミュレーション結果を保存
                </button>
              </div>
            </>
          )}

          {/* Saved Simulations */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-pink-500" />
              保存済みシミュレーション
            </h3>
            {historyLoading ? (
              <div className="text-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-gray-400 mx-auto" />
              </div>
            ) : history.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-gray-600">
                        商品名
                      </th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600">
                        販売価格
                      </th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600">
                        利益率
                      </th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600">
                        月間利益
                      </th>
                      <th className="text-right px-4 py-3 font-medium text-gray-600">
                        ROI
                      </th>
                      <th className="text-left px-4 py-3 font-medium text-gray-600">
                        日付
                      </th>
                      <th className="w-10"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {history.map((sim) => (
                      <tr key={sim.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium text-gray-900">
                          {sim.product_name || "—"}
                        </td>
                        <td className="px-4 py-3 text-right">
                          ¥{sim.selling_price.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {(sim.profit_margin * 100).toFixed(1)}%
                        </td>
                        <td className="px-4 py-3 text-right font-medium">
                          ¥{sim.monthly_profit.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {(sim.roi * 100).toFixed(1)}%
                        </td>
                        <td className="px-4 py-3 text-gray-500">
                          {new Date(sim.created_at).toLocaleDateString("ja-JP")}
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => handleDelete(sim.id)}
                            className="text-red-400 hover:text-red-600"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center py-8">
                保存済みのシミュレーションはありません
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

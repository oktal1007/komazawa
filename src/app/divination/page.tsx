"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";

const CATEGORY_MAP: Record<string, string> = {
  love: "恋愛",
  career: "仕事",
  money: "金運",
  general: "総合運",
};

const MENU_SUGGESTIONS: Record<string, string[]> = {
  恋愛: [
    "【運命の人発見鑑定】",
    "【恋愛成就鑑定】",
    "【復縁可能性鑑定】",
    "【相性徹底鑑定】",
    "【片思い成就鑑定】",
  ],
  仕事: [
    "【天職発見鑑定】",
    "【転職タイミング鑑定】",
    "【キャリアアップ鑑定】",
    "【独立開業鑑定】",
    "【職場人間関係鑑定】",
  ],
  金運: [
    "【金運開花鑑定】",
    "【財運アップ鑑定】",
    "【収入倍増鑑定】",
    "【投資運鑑定】",
    "【副業成功鑑定】",
  ],
  総合運: [
    "【人生総合鑑定】",
    "【運勢の流れ鑑定】",
    "【開運ロードマップ鑑定】",
    "【魂の使命鑑定】",
    "【年間運勢鑑定】",
  ],
};

interface PageData {
  page_role: string;
  text: string;
}

interface GeneratedContent {
  title: string;
  pages: PageData[];
}

interface FormData {
  customerName: string;
  birthYear: string;
  birthMonth: string;
  birthDay: string;
  birthHour: string;
  gender: string;
  category: string;
  menuName: string;
  consultationContent: string;
  additionalMemo: string;
  divinationMethods: string[];
}

function DivinationFormContent() {
  const searchParams = useSearchParams();
  const categoryParam = searchParams.get("category");

  const [form, setForm] = useState<FormData>({
    customerName: "",
    birthYear: "",
    birthMonth: "",
    birthDay: "",
    birthHour: "",
    gender: "",
    category: categoryParam ? (CATEGORY_MAP[categoryParam] || "") : "",
    menuName: "",
    consultationContent: "",
    additionalMemo: "",
    divinationMethods: [],
  });

  const [step, setStep] = useState<"form" | "generating" | "preview" | "exporting" | "done">("form");
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);
  const [calculations, setCalculations] = useState<Record<string, unknown> | null>(null);
  const [exportUrl, setExportUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (categoryParam && CATEGORY_MAP[categoryParam]) {
      setForm((prev) => ({ ...prev, category: CATEGORY_MAP[categoryParam] }));
    }
  }, [categoryParam]);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const updateForm = (field: keyof FormData, value: string | string[]) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const toggleMethod = (method: string) => {
    setForm((prev) => {
      if (method === "フルパッケージ") {
        return {
          ...prev,
          divinationMethods: prev.divinationMethods.includes(method)
            ? []
            : ["フルパッケージ"],
        };
      }
      const methods = prev.divinationMethods.filter(
        (m) => m !== "フルパッケージ"
      );
      if (methods.includes(method)) {
        return {
          ...prev,
          divinationMethods: methods.filter((m) => m !== method),
        };
      }
      return { ...prev, divinationMethods: [...methods, method] };
    });
  };

  const handleGenerate = async () => {
    setError(null);
    setStep("generating");

    try {
      const response = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_name: form.customerName,
          birth_year: parseInt(form.birthYear),
          birth_month: parseInt(form.birthMonth),
          birth_day: parseInt(form.birthDay),
          birth_hour: form.birthHour ? parseInt(form.birthHour) : null,
          gender: form.gender,
          category: form.category,
          menu_name: form.menuName,
          consultation_content: form.consultationContent,
          additional_memo: form.additionalMemo,
          divination_methods: form.divinationMethods,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "生成に失敗しました");
      }

      const data = await response.json();
      setGeneratedContent(data.generated_content);
      setCalculations(data.calculations);
      setStep("preview");
    } catch (e) {
      setError(e instanceof Error ? e.message : "エラーが発生しました");
      setStep("form");
    }
  };

  const handleExportPdf = async () => {
    if (!generatedContent) return;
    setError(null);
    setStep("exporting");

    try {
      const response = await fetch(`${API_BASE}/api/export-pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(generatedContent),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "PDF生成に失敗しました");
      }

      const data = await response.json();
      setExportUrl(data.export_url);
      setStep("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "エラーが発生しました");
      setStep("preview");
    }
  };

  const menuSuggestions = MENU_SUGGESTIONS[form.category] || [];

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <a
          href="/"
          className="text-[#c9a84c]/60 hover:text-[#c9a84c] text-sm transition-colors"
        >
          ← TOP
        </a>
        <h1 className="text-gold-gradient text-2xl font-bold">鑑定レポート作成</h1>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Step: Form */}
      {step === "form" && (
        <div className="space-y-6">
          {/* Customer Info */}
          <fieldset className="card-mystic rounded-xl p-6 space-y-4">
            <legend className="text-[#c9a84c] font-bold text-sm px-2">
              お客様情報
            </legend>

            <div>
              <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                お客様名（フルネーム）*
              </label>
              <input
                type="text"
                value={form.customerName}
                onChange={(e) => updateForm("customerName", e.target.value)}
                className="input-mystic w-full rounded-lg px-4 py-2.5 text-sm"
                placeholder="例：山田 花子"
              />
            </div>

            <div className="grid grid-cols-4 gap-3">
              <div>
                <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                  生年（西暦）*
                </label>
                <input
                  type="number"
                  value={form.birthYear}
                  onChange={(e) => updateForm("birthYear", e.target.value)}
                  className="input-mystic w-full rounded-lg px-3 py-2.5 text-sm"
                  placeholder="1990"
                />
              </div>
              <div>
                <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                  月*
                </label>
                <input
                  type="number"
                  value={form.birthMonth}
                  onChange={(e) => updateForm("birthMonth", e.target.value)}
                  className="input-mystic w-full rounded-lg px-3 py-2.5 text-sm"
                  placeholder="6"
                  min="1"
                  max="12"
                />
              </div>
              <div>
                <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                  日*
                </label>
                <input
                  type="number"
                  value={form.birthDay}
                  onChange={(e) => updateForm("birthDay", e.target.value)}
                  className="input-mystic w-full rounded-lg px-3 py-2.5 text-sm"
                  placeholder="15"
                  min="1"
                  max="31"
                />
              </div>
              <div>
                <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                  出生時刻
                </label>
                <input
                  type="number"
                  value={form.birthHour}
                  onChange={(e) => updateForm("birthHour", e.target.value)}
                  className="input-mystic w-full rounded-lg px-3 py-2.5 text-sm"
                  placeholder="14"
                  min="0"
                  max="23"
                />
              </div>
            </div>

            <div>
              <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                性別*
              </label>
              <div className="flex gap-3">
                {["女性", "男性", "その他"].map((g) => (
                  <button
                    key={g}
                    onClick={() => updateForm("gender", g)}
                    className={`rounded-lg px-4 py-2 text-sm transition-all ${
                      form.gender === g
                        ? "btn-gold"
                        : "border border-[rgba(201,168,76,0.3)] text-[#e8dcc8]/60 hover:border-[rgba(201,168,76,0.6)]"
                    }`}
                  >
                    {g}
                  </button>
                ))}
              </div>
            </div>
          </fieldset>

          {/* Divination Settings */}
          <fieldset className="card-mystic rounded-xl p-6 space-y-4">
            <legend className="text-[#c9a84c] font-bold text-sm px-2">
              鑑定設定
            </legend>

            <div>
              <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                鑑定カテゴリ*
              </label>
              <div className="flex flex-wrap gap-2">
                {["恋愛", "仕事", "金運", "総合運"].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => updateForm("category", cat)}
                    className={`rounded-lg px-4 py-2 text-sm transition-all ${
                      form.category === cat
                        ? "btn-gold"
                        : "border border-[rgba(201,168,76,0.3)] text-[#e8dcc8]/60 hover:border-[rgba(201,168,76,0.6)]"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                鑑定メニュー名*
              </label>
              <input
                type="text"
                value={form.menuName}
                onChange={(e) => updateForm("menuName", e.target.value)}
                className="input-mystic w-full rounded-lg px-4 py-2.5 text-sm"
                placeholder="例：【運命の人発見鑑定】"
              />
              {menuSuggestions.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {menuSuggestions.map((s) => (
                    <button
                      key={s}
                      onClick={() => updateForm("menuName", s)}
                      className="rounded-md bg-[rgba(201,168,76,0.1)] px-2 py-1 text-xs text-[#c9a84c]/70 hover:text-[#c9a84c] transition-colors"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                使用占術*
              </label>
              <div className="flex flex-wrap gap-2">
                {["数秘術", "西洋占星術", "四柱推命", "フルパッケージ"].map(
                  (method) => (
                    <button
                      key={method}
                      onClick={() => toggleMethod(method)}
                      className={`rounded-lg px-4 py-2 text-sm transition-all ${
                        form.divinationMethods.includes(method)
                          ? "btn-gold"
                          : "border border-[rgba(201,168,76,0.3)] text-[#e8dcc8]/60 hover:border-[rgba(201,168,76,0.6)]"
                      }`}
                    >
                      {method}
                    </button>
                  )
                )}
              </div>
            </div>
          </fieldset>

          {/* Consultation Content */}
          <fieldset className="card-mystic rounded-xl p-6 space-y-4">
            <legend className="text-[#c9a84c] font-bold text-sm px-2">
              相談内容
            </legend>

            <div>
              <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                お客様の相談内容（Mercariのやり取りをコピペ）*
              </label>
              <textarea
                value={form.consultationContent}
                onChange={(e) =>
                  updateForm("consultationContent", e.target.value)
                }
                className="input-mystic w-full rounded-lg px-4 py-2.5 text-sm min-h-[160px]"
                placeholder="お客様からのメッセージをそのまま貼り付けてください..."
              />
            </div>

            <div>
              <label className="block text-[#e8dcc8]/70 text-xs mb-1">
                追加メモ（自分用）
              </label>
              <textarea
                value={form.additionalMemo}
                onChange={(e) => updateForm("additionalMemo", e.target.value)}
                className="input-mystic w-full rounded-lg px-4 py-2.5 text-sm min-h-[80px]"
                placeholder="鑑定に反映したい追加情報やメモ..."
              />
            </div>
          </fieldset>

          {/* Submit */}
          <div className="text-center">
            <button
              onClick={handleGenerate}
              disabled={
                !form.customerName ||
                !form.birthYear ||
                !form.birthMonth ||
                !form.birthDay ||
                !form.gender ||
                !form.category ||
                !form.menuName ||
                !form.consultationContent ||
                form.divinationMethods.length === 0
              }
              className="btn-gold rounded-xl px-10 py-3 text-base disabled:opacity-40 disabled:cursor-not-allowed"
            >
              鑑定レポートを生成する
            </button>
          </div>
        </div>
      )}

      {/* Step: Generating */}
      {step === "generating" && (
        <div className="card-mystic rounded-xl p-12 text-center space-y-4">
          <div className="text-4xl animate-spin inline-block">🌙</div>
          <p className="text-[#c9a84c] font-bold">
            バステト女神の啓示を受信中...
          </p>
          <p className="text-[#e8dcc8]/50 text-sm">
            占術計算とAI鑑定文の生成を行っています。しばらくお待ちください。
          </p>
        </div>
      )}

      {/* Step: Preview */}
      {step === "preview" && generatedContent && (
        <div className="space-y-6">
          <div className="card-mystic rounded-xl p-6 space-y-4">
            <h2 className="text-gold-gradient text-xl font-bold">
              {generatedContent.title}
            </h2>

            {generatedContent.pages.map((page, idx) => (
              <div key={idx} className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="rounded-md bg-[rgba(201,168,76,0.2)] px-2 py-0.5 text-xs text-[#c9a84c]">
                    {page.page_role === "cover"
                      ? "P1 表紙"
                      : page.page_role === "closing"
                        ? `P${idx + 1} 締め`
                        : `P${idx + 1} 本文`}
                  </span>
                  <span className="text-[#e8dcc8]/30 text-xs">
                    {page.text.length}文字
                  </span>
                </div>
                <div className="rounded-lg bg-[rgba(10,10,26,0.6)] p-4">
                  <p className="text-[#e8dcc8]/80 text-sm leading-relaxed whitespace-pre-wrap">
                    {page.text}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Calculation Results */}
          {calculations && (
            <div className="card-mystic rounded-xl p-6 space-y-3">
              <h3 className="text-[#c9a84c] font-bold text-sm">占術計算結果</h3>
              <pre className="rounded-lg bg-[rgba(10,10,26,0.6)] p-4 text-[#e8dcc8]/60 text-xs overflow-x-auto">
                {JSON.stringify(calculations, null, 2)}
              </pre>
            </div>
          )}

          <div className="flex gap-4 justify-center">
            <button
              onClick={() => setStep("form")}
              className="rounded-xl border border-[rgba(201,168,76,0.4)] px-6 py-3 text-sm text-[#c9a84c] hover:bg-[rgba(201,168,76,0.1)] transition-colors"
            >
              ← 修正する
            </button>
            <button
              onClick={handleGenerate}
              className="rounded-xl border border-[rgba(201,168,76,0.4)] px-6 py-3 text-sm text-[#c9a84c] hover:bg-[rgba(201,168,76,0.1)] transition-colors"
            >
              再生成
            </button>
            <button
              onClick={handleExportPdf}
              className="btn-gold rounded-xl px-8 py-3 text-base"
            >
              PDF生成（Canva）
            </button>
          </div>
        </div>
      )}

      {/* Step: Exporting */}
      {step === "exporting" && (
        <div className="card-mystic rounded-xl p-12 text-center space-y-4">
          <div className="text-4xl animate-spin inline-block">📜</div>
          <p className="text-[#c9a84c] font-bold">
            Canva APIでPDF生成中...
          </p>
          <p className="text-[#e8dcc8]/50 text-sm">
            テンプレートへのテキスト流し込みとPDFエクスポートを行っています。
          </p>
        </div>
      )}

      {/* Step: Done */}
      {step === "done" && exportUrl && (
        <div className="card-mystic rounded-xl p-8 text-center space-y-6">
          <div className="text-5xl">✨</div>
          <h2 className="text-gold-gradient text-2xl font-bold">
            鑑定レポート完成
          </h2>
          <p className="text-[#e8dcc8]/60 text-sm">
            PDFの生成が完了しました。下のボタンからダウンロードしてください。
          </p>

          <div className="flex gap-4 justify-center">
            <a
              href={exportUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-gold rounded-xl px-8 py-3 text-base inline-block"
            >
              PDFをダウンロード
            </a>
            <button
              onClick={() => {
                setStep("form");
                setGeneratedContent(null);
                setCalculations(null);
                setExportUrl(null);
              }}
              className="rounded-xl border border-[rgba(201,168,76,0.4)] px-6 py-3 text-sm text-[#c9a84c] hover:bg-[rgba(201,168,76,0.1)] transition-colors"
            >
              新規作成
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DivinationPage() {
  return (
    <Suspense
      fallback={
        <div className="text-center py-12 text-[#e8dcc8]/50">読み込み中...</div>
      }
    >
      <DivinationFormContent />
    </Suspense>
  );
}

"use client";

import { useState } from "react";

const CATEGORIES = [
  {
    id: "love",
    name: "恋愛鑑定",
    icon: "💕",
    description: "恋愛運・相性・出会い・復縁",
    template: `この度は恋愛鑑定サービスをご購入いただき、誠にありがとうございます。
あなたの恋愛について詳しく鑑定させていただくために、以下の情報をお教えください。

【必要な情報】
1. 基本情報
・お名前（フルネーム）
・生年月日（西暦年月日）
・出生時刻（分かる範囲で結構です）

2. 恋愛の状況について
・現在の恋愛状況（恋人の有無、片思い、復縁希望など）
・恋愛鑑定を受けたいと思われた理由
・お悩みや知りたいこと（相性、今後の展開、出会いの時期など）
・特定の相手がいる場合は、その方との関係性

【鑑定の流れ】
情報をお教えいただいた後、2-3営業日以内に詳細な鑑定結果をお送りいたします。
あなたの恋愛運や相性、そして恋愛成就のためのアドバイスまで、心を込めて鑑定させていただきます。
ご質問がございましたら、お気軽にお声かけください。
あなたの恋愛が素敵な方向に向かうよう、全力でサポートさせていただきます。
※お教えいただいた情報は厳重に管理し、鑑定以外の目的では使用いたしません。`,
  },
  {
    id: "career",
    name: "仕事鑑定",
    icon: "💼",
    description: "仕事運・転職・適職・キャリア",
    template: `この度は仕事鑑定サービスをご購入いただき、誠にありがとうございます。
あなたのお仕事について詳しく鑑定させていただくために、以下の情報をお教えください。

【必要な情報】
1. 基本情報
・お名前（フルネーム）
・生年月日（西暦年月日）
・出生時刻（分かる範囲で結構です）

2. お仕事の状況について
・現在のお仕事の状況（職種、勤続年数など）
・仕事鑑定を受けたいと思われた理由
・お悩みや知りたいこと（転職時期、適職、人間関係、昇進など）
・今後のキャリアで望むこと

【鑑定の流れ】
情報をお教えいただいた後、2-3営業日以内に詳細な鑑定結果をお送りいたします。
あなたの仕事運や適職、そしてキャリア成功のためのアドバイスまで、心を込めて鑑定させていただきます。
ご質問がございましたら、お気軽にお声かけください。
あなたのお仕事が素晴らしい方向に向かうよう、全力でサポートさせていただきます。
※お教えいただいた情報は厳重に管理し、鑑定以外の目的では使用いたしません。`,
  },
  {
    id: "money",
    name: "金運鑑定",
    icon: "💰",
    description: "金運・財運・投資・収入アップ",
    template: `この度は金運鑑定サービスをご購入いただき、誠にありがとうございます。
あなたの金運について詳しく鑑定させていただくために、以下の情報をお教えください。

【必要な情報】
1. 基本情報
・お名前（フルネーム）
・生年月日（西暦年月日）
・出生時刻（分かる範囲で結構です）

2. 金運の状況について
・現在のお金に関する状況
・金運鑑定を受けたいと思われた理由
・お悩みや知りたいこと（収入アップ、投資、貯蓄、副業など）
・今後の経済面で望むこと

【鑑定の流れ】
情報をお教えいただいた後、2-3営業日以内に詳細な鑑定結果をお送りいたします。
あなたの金運や財運、そして豊かさを引き寄せるためのアドバイスまで、心を込めて鑑定させていただきます。
ご質問がございましたら、お気軽にお声かけください。
あなたの金運が大きく開花するよう、全力でサポートさせていただきます。
※お教えいただいた情報は厳重に管理し、鑑定以外の目的では使用いたしません。`,
  },
  {
    id: "general",
    name: "総合運鑑定",
    icon: "🔮",
    description: "総合運・人生全般・運勢の流れ",
    template: `この度は総合運鑑定サービスをご購入いただき、誠にありがとうございます。
あなたの運勢について詳しく鑑定させていただくために、以下の情報をお教えください。

【必要な情報】
1. 基本情報
・お名前（フルネーム）
・生年月日（西暦年月日）
・出生時刻（分かる範囲で結構です）

2. 現在の状況について
・今、最も気になっていること
・総合運鑑定を受けたいと思われた理由
・お悩みや知りたいこと（全体的な運勢の流れ、人生の転機、開運法など）
・今後の人生で望むこと

【鑑定の流れ】
情報をお教えいただいた後、2-3営業日以内に詳細な鑑定結果をお送りいたします。
あなたの総合運や人生の流れ、そして開運のためのアドバイスまで、心を込めて鑑定させていただきます。
ご質問がございましたら、お気軽にお声かけください。
あなたの人生が輝きに満ちたものとなるよう、全力でサポートさせていただきます。
※お教えいただいた情報は厳重に管理し、鑑定以外の目的では使用いたしません。`,
  },
];

export default function TopPage() {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = async (categoryId: string, template: string) => {
    await navigator.clipboard.writeText(template);
    setCopiedId(categoryId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-10">
      {/* Hero */}
      <section className="text-center space-y-4 py-8">
        <div className="text-5xl">🐱</div>
        <h1 className="text-gold-gradient text-3xl font-bold">
          バステト神AI占い鑑定レポート
        </h1>
        <p className="text-[#e8dcc8]/60 text-sm max-w-lg mx-auto leading-relaxed">
          古代エジプトの女神バステトの化身として、月の満ち欠けに合わせた霊視と
          数千年の叡智によってお客様の運命を鑑定いたします。
        </p>
      </section>

      {/* Category Cards */}
      <section className="space-y-4">
        <h2 className="text-[#c9a84c] text-lg font-bold">
          鑑定カテゴリ — ヒアリングテンプレート
        </h2>
        <p className="text-[#e8dcc8]/50 text-sm">
          カテゴリを選んでヒアリングテンプレートをコピーし、Mercariのお客様へ送信してください。
        </p>

        <div className="grid gap-4 sm:grid-cols-2">
          {CATEGORIES.map((cat) => (
            <div key={cat.id} className="card-mystic rounded-xl p-6 space-y-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{cat.icon}</span>
                <div>
                  <h3 className="text-[#c9a84c] font-bold">{cat.name}</h3>
                  <p className="text-[#e8dcc8]/50 text-xs">{cat.description}</p>
                </div>
              </div>

              <div className="bg-[rgba(10,10,26,0.6)] rounded-lg p-3 max-h-32 overflow-y-auto">
                <pre className="text-[#e8dcc8]/70 text-xs whitespace-pre-wrap font-[inherit] leading-relaxed">
                  {cat.template}
                </pre>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => handleCopy(cat.id, cat.template)}
                  className="btn-gold rounded-lg px-4 py-2 text-sm flex-1"
                >
                  {copiedId === cat.id
                    ? "✓ コピーしました"
                    : "テンプレートをコピー"}
                </button>
                <a
                  href={`/divination?category=${cat.id}`}
                  className="rounded-lg border border-[rgba(201,168,76,0.4)] px-4 py-2 text-sm text-[#c9a84c] hover:bg-[rgba(201,168,76,0.1)] transition-colors text-center"
                >
                  鑑定作成 →
                </a>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Quick Start */}
      <section className="text-center py-6">
        <a
          href="/divination"
          className="btn-gold inline-block rounded-xl px-8 py-3 text-base"
        >
          鑑定レポートを作成する
        </a>
      </section>
    </div>
  );
}

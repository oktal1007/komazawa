# バステト神AI占い鑑定レポート自動生成システム — 引き継ぎ資料

## 1. プロジェクト概要

Mercariで占いサービスを提供するための鑑定レポート自動生成Webアプリ。
「月花の守猫 バステリア・ルア」（バステト神）としてお客様の運命を鑑定し、
Canvaテンプレートを使ったPDFレポートを自動生成する。

---

## 2. リポジトリ情報

| 項目 | 値 |
|------|-----|
| リポジトリ | `oktal1007/komazawa` |
| ブランチ | `claude/bastet-divination-canva-4fGpm` |
| 最新コミット | `feat: バステト神AI占い鑑定レポート自動生成システム（Canva連携版）` |

```bash
git clone <リポジトリURL>
cd komazawa
git checkout claude/bastet-divination-canva-4fGpm
```

---

## 3. 技術スタック

| レイヤー | 技術 |
|----------|------|
| Frontend | Next.js 16 (App Router) + TypeScript + Tailwind CSS 4 |
| Backend | Python FastAPI |
| AI生成 | Anthropic Claude API (`claude-sonnet-4-20250514`) |
| PDF生成 | Canva API（テンプレートID: `DAG6v4MOJZ8`） |

---

## 4. ディレクトリ構成

```
komazawa/
├── backend/                    # Python FastAPI バックエンド
│   ├── main.py                 # FastAPIエントリポイント（3つのAPIエンドポイント）
│   ├── requirements.txt        # Python依存パッケージ
│   ├── data/
│   │   ├── numerology.json     # 数秘術データ（バステト神世界観）
│   │   └── four_pillars.json   # 四柱推命データ（十干十二支・五行）
│   └── services/
│       ├── numerology.py       # 数秘術計算
│       ├── astrology.py        # 西洋占星術計算（Swiss Ephemeris対応）
│       ├── four_pillars.py     # 四柱推命計算
│       ├── divination_generator.py  # Claude API鑑定文生成
│       └── canva_exporter.py   # Canva API連携PDF生成
│
├── src/                        # Next.js フロントエンド
│   └── app/
│       ├── layout.tsx          # ルートレイアウト（エジプシャンテーマUI）
│       ├── globals.css         # グローバルCSS（金×紫×深青カラースキーム）
│       ├── page.tsx            # TOP画面（カテゴリ選択+テンプレートコピー）
│       ├── divination/
│       │   └── page.tsx        # 鑑定作成画面（フォーム→生成→プレビュー→PDF）
│       └── api/
│           ├── generate/route.ts    # Backend proxy
│           └── export-pdf/route.ts  # Backend proxy
│
├── next.config.ts              # API rewrites設定
├── package.json
├── .env.local.example          # 環境変数テンプレート
└── .gitignore
```

---

## 5. セットアップ手順

### 5-1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5-2. Frontend

```bash
cd komazawa
npm install
```

### 5-3. 環境変数

```bash
cp .env.local.example .env.local
```

`.env.local` に以下を設定：

```
NEXT_PUBLIC_API_URL=http://localhost:8000
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
CANVA_ACCESS_TOKEN=<Canva APIトークン>
FRONTEND_URL=http://localhost:3000
```

### 5-4. 起動

```bash
# ターミナル1: Backend (http://localhost:8000)
cd backend && source .venv/bin/activate && python main.py

# ターミナル2: Frontend (http://localhost:3000)
npm run dev
```

---

## 6. APIエンドポイント一覧

| メソッド | パス | 機能 |
|----------|------|------|
| GET | `/api/health` | ヘルスチェック |
| POST | `/api/calculate` | 占術計算のみ実行 |
| POST | `/api/generate` | 占術計算 + Claude API鑑定文生成 |
| POST | `/api/export-pdf` | Canva APIでPDFエクスポート |

### リクエスト例（`/api/generate`）

```json
{
  "customer_name": "山田 花子",
  "birth_year": 1990,
  "birth_month": 6,
  "birth_day": 15,
  "birth_hour": 14,
  "gender": "女性",
  "category": "恋愛",
  "menu_name": "【運命の人発見鑑定】",
  "consultation_content": "お客様からの相談内容...",
  "additional_memo": "",
  "divination_methods": ["数秘術", "西洋占星術"]
}
```

---

## 7. Canvaテンプレート情報

| 項目 | 値 |
|------|-----|
| デザインID | `DAG6v4MOJZ8` |
| ページ数 | 3ページ（表紙・本文・締め） |

### テキスト要素ID

| ページ | 役割 | element_id |
|--------|------|------------|
| P1 | タイトル | `PBx2BHqMdxJNYGVP-LBbBrHppq9mszHmg` |
| P1 | 本文 | `PBx2BHqMdxJNYGVP-LB8m5N4GQ9blRpg9` |
| P2 | 本文 | `PBgC1zdZRkBJfKS7-LB3H1nylMY8VYplS` |
| P3 | 本文 | `PBK1qmHJX42BVY9N-LB6gxw9RKzsJHJCh` |

### 文字数上限

- P1本文：約600文字
- P2本文：約900文字
- P3本文：約800文字
- 追加ページ：約900文字

---

## 8. 鑑定文生成の仕組み

### フロー

```
フォーム入力 → 占術計算（数秘術/西洋占星術/四柱推命）
    → Claude APIに計算結果+相談内容を送信
    → JSON形式で鑑定文を受け取り（pages配列）
    → プレビュー表示
    → Canvaテンプレートにテキスト流し込み
    → PDFエクスポート → ダウンロード
```

### Claude APIが返すJSON構造

```json
{
  "title": "バステト女神からの【鑑定メニュー名】",
  "pages": [
    {"page_role": "cover", "text": "P1本文（600字以内）"},
    {"page_role": "body", "text": "P2本文（900字以内）"},
    {"page_role": "body", "text": "追加ページ（900字以内）"},
    {"page_role": "closing", "text": "最終ページ（800字以内・署名付き）"}
  ]
}
```

### 鑑定7ステップ構文

1. 共感・寄り添い・受容・理解
2. 結論「明るい展望」の宣言
3. 明るい展望の理由（占術結果を根拠に）
4. 悩みの原因（世界観的・超常的解釈）
5. 解決策・行動提案（具体的な場所・タイミング含む）
6. 明るい未来のビジョンを情景描写
7. セールストーク（自然な追加鑑定への誘導）

---

## 9. 現在のステータスと未対応事項

### 完了済み
- [x] Python占術計算エンジン3種（数秘術・西洋占星術・四柱推命）
- [x] Claude API鑑定文生成（システムプロンプト・7ステップ構文）
- [x] Canva API連携（テンプレートコピー→テキスト差替→PDF出力）
- [x] Next.js TOP画面（4カテゴリ・ヒアリングテンプレートコピー）
- [x] Next.js 鑑定作成画面（フォーム→生成→プレビュー→PDF出力）
- [x] ビルド確認済み（`next build` 成功）

### 未対応・今後の課題
- [ ] APIキー（Anthropic / Canva）の実環境設定と動作確認
- [ ] Canva APIの追加ページ複製時のelement_id取得（実APIレスポンス確認が必要）
- [ ] エラーハンドリングの強化（ネットワークエラー・タイムアウト等）
- [ ] 鑑定履歴の保存機能（DB未導入）
- [ ] 本番デプロイ（Vercel + Railway等）
- [ ] 認証機能（自分専用ツールのため優先度低）

---

## 10. 必要なAPIキーの取得先

| サービス | 取得先 | 備考 |
|----------|--------|------|
| Anthropic Claude API | https://console.anthropic.com/ | `claude-sonnet-4-20250514` を使用 |
| Canva Connect API | https://www.canva.com/developers/ | Design APIの有効化が必要 |

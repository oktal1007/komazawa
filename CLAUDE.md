# バステト神AI占い鑑定レポート自動生成システム — OpenClaw引き継ぎ

## プロジェクト概要

Mercariで占いサービスを提供するための鑑定レポート自動生成Webアプリ。
「月花の守猫 バステリア・ルア」（バステト神）としてお客様の運命を鑑定し、
Canvaテンプレートを使ったPDFレポートを自動生成する。

## リポジトリ・ブランチ

- リポジトリ: `oktal1007/komazawa`
- ブランチ: `claude/bastet-divination-canva-4fGpm`
- 最新コミット: `feat: デプロイ構成を追加 (Vercel + Render)` (61ab480)

## 技術スタック

- **Frontend**: Next.js 16 (App Router) + TypeScript + Tailwind CSS 4
- **Backend**: Python 3.12 + FastAPI + Uvicorn
- **AI生成**: Anthropic Claude API (`claude-sonnet-4-20250514`)
- **PDF生成**: Canva Connect API（OAuth 2.0 + PKCE）
- **デプロイ**: Vercel (Frontend) + Render (Backend/Docker)

## ディレクトリ構成

```
komazawa/
├── backend/                         # Python FastAPI バックエンド
│   ├── main.py                      # FastAPIエントリポイント
│   ├── Dockerfile                   # Render用Docker設定
│   ├── requirements.txt             # Python依存 (fastapi, anthropic, pyswisseph等)
│   ├── data/
│   │   ├── numerology.json          # 数秘術データ（バステト神世界観）
│   │   └── four_pillars.json        # 四柱推命データ（十干十二支・五行）
│   └── services/
│       ├── numerology.py            # 数秘術計算
│       ├── astrology.py             # 西洋占星術計算（Swiss Ephemeris）
│       ├── four_pillars.py          # 四柱推命計算
│       ├── divination_generator.py  # Claude API鑑定文生成（7ステップ構文）
│       ├── canva_exporter.py        # Canva API連携PDF生成
│       └── canva_oauth.py           # Canva OAuth 2.0 + PKCE
│
├── src/app/                         # Next.js フロントエンド
│   ├── layout.tsx                   # ルートレイアウト（エジプシャンテーマ）
│   ├── globals.css                  # グローバルCSS（金×紫×深青カラー）
│   ├── page.tsx                     # TOP画面（カテゴリ選択）
│   ├── divination/page.tsx          # 鑑定作成画面（フォーム→生成→プレビュー→PDF）
│   └── api/                         # Next.js API Routes（Backend proxy）
│       ├── generate/route.ts
│       ├── export-pdf/route.ts
│       └── canva/{authorize,callback,status}/route.ts
│
├── render.yaml                      # Render Blueprint設定
├── vercel.json                      # Vercelリライト設定
├── next.config.ts                   # Next.js設定
└── HANDOVER.md                      # 詳細引き継ぎ資料
```

## ローカル開発セットアップ（Mac）

### 前提条件
- Node.js 18以上
- Python 3.12
- Git

### バックエンド
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py   # http://localhost:8000
```

### フロントエンド
```bash
npm install
npm run dev      # http://localhost:3000
```

### 環境変数（`.env.local`）
```
NEXT_PUBLIC_API_URL=http://localhost:8000
ANTHROPIC_API_KEY=sk-ant-xxxxx
CANVA_CLIENT_ID=（Canva Developersで取得）
CANVA_CLIENT_SECRET=（Canva Developersで取得）
CANVA_REDIRECT_URI=http://127.0.0.1:8000/api/canva/callback
FRONTEND_URL=http://localhost:3000
```

## APIエンドポイント

| メソッド | パス | 機能 |
|----------|------|------|
| GET | `/api/health` | ヘルスチェック |
| POST | `/api/calculate` | 占術計算のみ |
| POST | `/api/generate` | 占術計算 + Claude API鑑定文生成 |
| POST | `/api/export-pdf` | Canva PDFエクスポート |
| GET | `/api/canva/authorize` | Canva OAuth認可URL取得 |
| GET | `/api/canva/callback` | Canva OAuthコールバック |
| GET | `/api/canva/status` | Canva認証状態確認 |

## デプロイ構成

### Render（バックエンド）
- `render.yaml` でBlueprint自動構成済み
- Docker runtime（`backend/Dockerfile`）
- 環境変数5つ: `ANTHROPIC_API_KEY`, `CANVA_CLIENT_ID`, `CANVA_CLIENT_SECRET`, `CANVA_REDIRECT_URI`, `FRONTEND_URL`

### Vercel（フロントエンド）
- `vercel.json` でAPIリライト設定済み
- 環境変数: `BACKEND_API_URL`（RenderのURL）

## 現在の進捗

### 完了済み
- Python占術計算エンジン3種（数秘術・西洋占星術・四柱推命）
- Claude API鑑定文生成（システムプロンプト・7ステップ構文）
- Canva OAuth 2.0 + PKCE認証フロー
- Canva API連携（テンプレートコピー→テキスト差替→PDF出力）
- Next.js TOP画面（4カテゴリ・ヒアリングテンプレートコピー）
- Next.js 鑑定作成画面（フォーム→生成→プレビュー→PDF出力）
- デプロイ構成ファイル（Vercel + Render）
- ビルド確認済み（`next build` 成功）

### 未対応・次のステップ
- [ ] Render + Vercelへの実デプロイと動作確認
- [ ] APIキー（Anthropic / Canva）の実環境設定
- [ ] Canva APIの追加ページ複製時のelement_id取得（実APIレスポンス確認が必要）
- [ ] エラーハンドリングの強化（ネットワークエラー・タイムアウト等）
- [ ] 鑑定履歴の保存機能（DB未導入）
- [ ] 認証機能（自分専用ツールのため優先度低）

## Canvaテンプレート情報

- デザインID: `DAG6v4MOJZ8`（3ページ構成：表紙・本文・締め）
- テキスト要素ID → `HANDOVER.md` のセクション7参照
- 文字数上限: P1=600字, P2=900字, P3=800字, 追加=900字

## コーディング規約
- フロントエンド: TypeScript strict, App Router規約に従う
- バックエンド: Python 3.12, type hints使用, FastAPIのPydanticモデル
- コミットメッセージ: `feat:` / `fix:` / `chore:` / `docs:` プレフィックス（日本語OK）

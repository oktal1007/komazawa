---
title: "Next.js入門 - モダンWebアプリケーション開発の始め方"
description: "Next.jsを使ったWebアプリケーション開発の基礎を解説します。環境構築からデプロイまで、実践的なステップで学びましょう。"
date: "2026-02-20"
category: "プログラミング"
tags: ["Next.js", "React", "TypeScript", "Web開発"]
thumbnail: "/images/nextjs-guide.webp"
affiliateLinks:
  - label: "Reactハンズオンラーニング 第2版"
    url: "https://www.amazon.co.jp/dp/4873119693"
    provider: "amazon"
  - label: "プロを目指す人のためのTypeScript入門"
    url: "https://www.amazon.co.jp/dp/4297127474"
    provider: "amazon"
published: true
---

## Next.jsとは

Next.jsは、Reactベースのフルスタックフレームワークです。サーバーサイドレンダリング（SSR）、静的サイト生成（SSG）、APIルートなど、モダンなWeb開発に必要な機能が揃っています。

## なぜNext.jsを選ぶのか

1. **SEOに強い** - サーバーサイドレンダリングにより、検索エンジンがコンテンツを正しくインデックスできます
2. **パフォーマンス** - 自動的なコード分割と画像最適化
3. **開発者体験** - ホットリロード、TypeScriptサポート、直感的なルーティング
4. **Vercelとの統合** - ワンクリックデプロイ

## 環境構築

まず、Node.js（v18以上）がインストールされていることを確認してください。

```bash
npx create-next-app@latest my-app --typescript --tailwind --app
cd my-app
npm run dev
```

これだけでローカル開発サーバーが起動します。`http://localhost:3000` にアクセスして確認しましょう。

## プロジェクト構成

```
my-app/
├── src/
│   ├── app/
│   │   ├── layout.tsx    # ルートレイアウト
│   │   ├── page.tsx      # トップページ
│   │   └── globals.css   # グローバルCSS
│   ├── components/       # コンポーネント
│   └── lib/              # ユーティリティ
├── public/               # 静的ファイル
├── package.json
└── tsconfig.json
```

## App Routerの基本

Next.js 13以降のApp Routerでは、ファイルシステムベースのルーティングが採用されています。

```typescript
// src/app/about/page.tsx
export default function AboutPage() {
  return <h1>About</h1>;
}
```

`src/app/about/page.tsx` を作成するだけで、`/about` ルートが自動的に生成されます。

## データフェッチ

Server Componentsを活用して、サーバー側でデータを取得できます。

```typescript
async function getData() {
  const res = await fetch('https://api.example.com/data');
  return res.json();
}

export default async function Page() {
  const data = await getData();
  return <div>{data.title}</div>;
}
```

## まとめ

Next.jsは、個人開発から大規模プロジェクトまで幅広く活用できるフレームワークです。この記事を参考に、ぜひ最初のプロジェクトを作成してみてください。

---
title: "Tailwind CSS実践テクニック - 効率的なスタイリングのコツ"
description: "Tailwind CSSを使ったWeb開発の実践的なテクニックとベストプラクティスを紹介します。"
date: "2026-02-15"
category: "プログラミング"
tags: ["Tailwind CSS", "CSS", "Web開発", "デザイン"]
thumbnail: "/images/tailwindcss-tips.webp"
affiliateLinks:
  - label: "Web制作者のためのCSS設計の教科書"
    url: "https://www.amazon.co.jp/dp/example3"
    provider: "amazon"
published: true
---

## Tailwind CSSとは

Tailwind CSSは、ユーティリティファーストのCSSフレームワークです。HTMLに直接クラスを記述することで、素早くスタイリングが行えます。

## 基本的な使い方

```html
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <h2 class="text-xl font-bold text-gray-800">タイトル</h2>
  <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    ボタン
  </button>
</div>
```

## レスポンシブデザイン

Tailwindでは、ブレークポイントプレフィックスで簡単にレスポンシブ対応ができます。

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- カード -->
</div>
```

- `sm:` - 640px以上
- `md:` - 768px以上
- `lg:` - 1024px以上
- `xl:` - 1280px以上

## ダークモード対応

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  ダークモード対応コンテンツ
</div>
```

## カスタムカラーの設定

`tailwind.config.ts` でプロジェクト固有のカラーパレットを定義できます。

```typescript
export default {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a5f',
        },
      },
    },
  },
};
```

## よく使うパターン

### カードコンポーネント

```html
<article class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition hover:shadow-lg">
  <img class="h-48 w-full object-cover" src="..." alt="..." />
  <div class="p-5">
    <h3 class="text-lg font-semibold">記事タイトル</h3>
    <p class="mt-2 text-sm text-gray-600">記事の説明文...</p>
  </div>
</article>
```

### ナビゲーション

```html
<nav class="sticky top-0 z-50 backdrop-blur-md bg-white/80 border-b">
  <div class="mx-auto max-w-7xl px-4 flex items-center justify-between h-16">
    <!-- ナビゲーションの中身 -->
  </div>
</nav>
```

## まとめ

Tailwind CSSはユーティリティクラスのアプローチにより、一貫性のあるデザインを高速に構築できます。最初は戸惑うかもしれませんが、慣れれば開発速度が大幅に向上します。

import Link from "next/link";
import { Metadata } from "next";
import { getAllCategories, getPostsByCategory } from "@/lib/content";

export const metadata: Metadata = {
  title: "カテゴリ一覧",
  description: "記事カテゴリの一覧ページです。",
};

export default function CategoriesPage() {
  const categories = getAllCategories();

  return (
    <div className="mx-auto max-w-5xl px-4 py-12">
      <h1 className="mb-8 text-3xl font-extrabold text-gray-900">
        カテゴリ一覧
      </h1>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {categories.map((category) => {
          const posts = getPostsByCategory(category);
          return (
            <Link
              key={category}
              href={`/categories/${encodeURIComponent(category)}`}
              className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-lg"
            >
              <h2 className="text-xl font-bold text-gray-900">{category}</h2>
              <p className="mt-2 text-sm text-gray-500">
                {posts.length}件の記事
              </p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

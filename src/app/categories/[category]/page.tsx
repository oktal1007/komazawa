import { Metadata } from "next";
import { getAllCategories, getPostsByCategory } from "@/lib/content";
import { PostCard } from "@/components/ui/PostCard";

interface PageProps {
  params: Promise<{ category: string }>;
}

export async function generateStaticParams() {
  return getAllCategories().map((category) => ({
    category: encodeURIComponent(category),
  }));
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { category } = await params;
  const decodedCategory = decodeURIComponent(category);
  return {
    title: `${decodedCategory}の記事一覧`,
    description: `${decodedCategory}カテゴリの記事一覧です。`,
  };
}

export default async function CategoryPage({ params }: PageProps) {
  const { category } = await params;
  const decodedCategory = decodeURIComponent(category);
  const posts = getPostsByCategory(decodedCategory);

  return (
    <div className="mx-auto max-w-5xl px-4 py-12">
      <h1 className="mb-8 text-3xl font-extrabold text-gray-900">
        {decodedCategory}
      </h1>
      {posts.length > 0 ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {posts.map((post) => (
            <PostCard key={post.slug} post={post} />
          ))}
        </div>
      ) : (
        <p className="text-gray-500">このカテゴリにはまだ記事がありません。</p>
      )}
    </div>
  );
}

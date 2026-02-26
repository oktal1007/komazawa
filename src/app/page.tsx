import { getAllPosts } from "@/lib/content";
import { PostCard } from "@/components/ui/PostCard";
import { siteConfig } from "@/lib/config";

export default function HomePage() {
  const posts = getAllPosts();

  return (
    <div className="mx-auto max-w-5xl px-4 py-12">
      {/* Hero Section */}
      <section className="mb-12 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">
          {siteConfig.title}
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
          {siteConfig.description}
        </p>
      </section>

      {/* Latest Posts */}
      <section>
        <h2 className="mb-6 text-2xl font-bold text-gray-900">最新記事</h2>
        {posts.length > 0 ? (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {posts.map((post) => (
              <PostCard key={post.slug} post={post} />
            ))}
          </div>
        ) : (
          <p className="text-gray-500">記事がまだありません。</p>
        )}
      </section>
    </div>
  );
}

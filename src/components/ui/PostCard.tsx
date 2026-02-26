import Link from "next/link";
import { format } from "date-fns";
import { ja } from "date-fns/locale";
import { Post } from "@/types";

interface PostCardProps {
  post: Post;
}

export function PostCard({ post }: PostCardProps) {
  const { slug, frontmatter } = post;

  return (
    <article className="group overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-lg">
      <Link href={`/posts/${slug}`}>
        <div className="h-48 bg-gradient-to-br from-blue-400 to-purple-500" />
        <div className="p-5">
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
              {frontmatter.category}
            </span>
            <time
              className="text-xs text-gray-500"
              dateTime={frontmatter.date}
            >
              {format(new Date(frontmatter.date), "yyyy年M月d日", {
                locale: ja,
              })}
            </time>
          </div>
          <h2 className="mt-3 text-lg font-bold text-gray-900 group-hover:text-blue-600">
            {frontmatter.title}
          </h2>
          <p className="mt-2 line-clamp-2 text-sm text-gray-600">
            {frontmatter.description}
          </p>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {frontmatter.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      </Link>
    </article>
  );
}

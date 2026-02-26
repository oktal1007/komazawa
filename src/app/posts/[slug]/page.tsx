import { Metadata } from "next";
import { notFound } from "next/navigation";
import { format } from "date-fns";
import { ja } from "date-fns/locale";
import { getAllSlugs, getPostWithHtml } from "@/lib/content";
import { ArticleJsonLd } from "@/components/seo/JsonLd";
import { AffiliateCard } from "@/components/revenue/AffiliateCard";
import { AdUnit } from "@/components/revenue/AdSense";
import { siteConfig } from "@/lib/config";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  return getAllSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPostWithHtml(slug);
  if (!post) return {};

  return {
    title: post.frontmatter.title,
    description: post.frontmatter.description,
    openGraph: {
      title: post.frontmatter.title,
      description: post.frontmatter.description,
      type: "article",
      publishedTime: post.frontmatter.date,
      modifiedTime: post.frontmatter.updatedAt || post.frontmatter.date,
      tags: post.frontmatter.tags,
      images: post.frontmatter.thumbnail
        ? [{ url: post.frontmatter.thumbnail }]
        : [],
    },
    twitter: {
      card: "summary_large_image",
      title: post.frontmatter.title,
      description: post.frontmatter.description,
    },
  };
}

export default async function PostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = await getPostWithHtml(slug);

  if (!post) notFound();

  return (
    <article className="mx-auto max-w-3xl px-4 py-12">
      <ArticleJsonLd frontmatter={post.frontmatter} slug={slug} />

      {/* Article Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
            {post.frontmatter.category}
          </span>
          <time
            className="text-sm text-gray-500"
            dateTime={post.frontmatter.date}
          >
            {format(new Date(post.frontmatter.date), "yyyy年M月d日", {
              locale: ja,
            })}
          </time>
        </div>
        <h1 className="mt-4 text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
          {post.frontmatter.title}
        </h1>
        <p className="mt-3 text-lg text-gray-600">
          {post.frontmatter.description}
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {post.frontmatter.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600"
            >
              #{tag}
            </span>
          ))}
        </div>
      </header>

      {/* Ad: Top */}
      <AdUnit slot="top-article" />

      {/* Article Content */}
      <div
        className="article-content"
        dangerouslySetInnerHTML={{ __html: post.contentHtml }}
      />

      {/* Affiliate Links */}
      {post.frontmatter.affiliateLinks && (
        <AffiliateCard links={post.frontmatter.affiliateLinks} />
      )}

      {/* Ad: Bottom */}
      <AdUnit slot="bottom-article" />

      {/* Author Info */}
      <div className="mt-12 rounded-xl border border-gray-200 bg-gray-50 p-6">
        <p className="text-sm font-medium text-gray-500">この記事を書いた人</p>
        <p className="mt-1 text-lg font-bold text-gray-900">
          {siteConfig.author}
        </p>
        <p className="mt-1 text-sm text-gray-600">{siteConfig.description}</p>
      </div>
    </article>
  );
}

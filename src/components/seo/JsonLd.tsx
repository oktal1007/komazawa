import { siteConfig } from "@/lib/config";
import { PostFrontmatter } from "@/types";

interface ArticleJsonLdProps {
  frontmatter: PostFrontmatter;
  slug: string;
}

export function ArticleJsonLd({ frontmatter, slug }: ArticleJsonLdProps) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: frontmatter.title,
    description: frontmatter.description,
    datePublished: frontmatter.date,
    dateModified: frontmatter.updatedAt || frontmatter.date,
    author: {
      "@type": "Person",
      name: siteConfig.author,
    },
    publisher: {
      "@type": "Organization",
      name: siteConfig.title,
    },
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": `${siteConfig.url}/posts/${slug}`,
    },
    image: frontmatter.thumbnail
      ? `${siteConfig.url}${frontmatter.thumbnail}`
      : undefined,
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  );
}

export function WebsiteJsonLd() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: siteConfig.title,
    description: siteConfig.description,
    url: siteConfig.url,
    publisher: {
      "@type": "Organization",
      name: siteConfig.title,
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  );
}

import { MetadataRoute } from "next";
import { getAllPosts, getAllCategories } from "@/lib/content";
import { siteConfig } from "@/lib/config";

export default function sitemap(): MetadataRoute.Sitemap {
  const posts = getAllPosts();
  const categories = getAllCategories();

  const postEntries: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${siteConfig.url}/posts/${post.slug}`,
    lastModified: new Date(
      post.frontmatter.updatedAt || post.frontmatter.date
    ),
    changeFrequency: "weekly",
    priority: 0.8,
  }));

  const categoryEntries: MetadataRoute.Sitemap = categories.map(
    (category) => ({
      url: `${siteConfig.url}/categories/${encodeURIComponent(category)}`,
      changeFrequency: "weekly",
      priority: 0.5,
    })
  );

  return [
    {
      url: siteConfig.url,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: `${siteConfig.url}/about`,
      changeFrequency: "monthly",
      priority: 0.3,
    },
    ...postEntries,
    ...categoryEntries,
  ];
}

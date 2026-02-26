import { Feed } from "feed";
import { getAllPosts } from "@/lib/content";
import { siteConfig } from "@/lib/config";

export async function GET() {
  const posts = getAllPosts();

  const feed = new Feed({
    title: siteConfig.title,
    description: siteConfig.description,
    id: siteConfig.url,
    link: siteConfig.url,
    language: "ja",
    copyright: `All rights reserved ${new Date().getFullYear()}, ${siteConfig.title}`,
    author: {
      name: siteConfig.author,
    },
  });

  posts.forEach((post) => {
    feed.addItem({
      title: post.frontmatter.title,
      id: `${siteConfig.url}/posts/${post.slug}`,
      link: `${siteConfig.url}/posts/${post.slug}`,
      description: post.frontmatter.description,
      date: new Date(post.frontmatter.date),
      category: [{ name: post.frontmatter.category }],
    });
  });

  return new Response(feed.rss2(), {
    headers: {
      "Content-Type": "application/xml",
    },
  });
}

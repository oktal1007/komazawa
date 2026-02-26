import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { remark } from "remark";
import html from "remark-html";
import { Post, PostFrontmatter } from "@/types";

const postsDirectory = path.join(process.cwd(), "src/content/posts");

export function getAllSlugs(): string[] {
  if (!fs.existsSync(postsDirectory)) return [];
  return fs
    .readdirSync(postsDirectory)
    .filter((file) => file.endsWith(".md"))
    .map((file) => file.replace(/\.md$/, ""));
}

export function getPostBySlug(slug: string): Post | null {
  const filePath = path.join(postsDirectory, `${slug}.md`);
  if (!fs.existsSync(filePath)) return null;

  const fileContents = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(fileContents);

  return {
    slug,
    frontmatter: data as PostFrontmatter,
    content,
  };
}

export async function getPostWithHtml(
  slug: string
): Promise<(Post & { contentHtml: string }) | null> {
  const post = getPostBySlug(slug);
  if (!post) return null;

  const processedContent = await remark().use(html).process(post.content);

  return {
    ...post,
    contentHtml: processedContent.toString(),
  };
}

export function getAllPosts(): Post[] {
  const slugs = getAllSlugs();
  return slugs
    .map((slug) => getPostBySlug(slug))
    .filter((post): post is Post => post !== null && post.frontmatter.published)
    .sort(
      (a, b) =>
        new Date(b.frontmatter.date).getTime() -
        new Date(a.frontmatter.date).getTime()
    );
}

export function getPostsByCategory(category: string): Post[] {
  return getAllPosts().filter(
    (post) => post.frontmatter.category === category
  );
}

export function getPostsByTag(tag: string): Post[] {
  return getAllPosts().filter((post) => post.frontmatter.tags.includes(tag));
}

export function getAllCategories(): string[] {
  const posts = getAllPosts();
  const categories = new Set(posts.map((post) => post.frontmatter.category));
  return Array.from(categories);
}

export function getAllTags(): string[] {
  const posts = getAllPosts();
  const tags = new Set(posts.flatMap((post) => post.frontmatter.tags));
  return Array.from(tags);
}

export interface PostFrontmatter {
  title: string;
  description: string;
  date: string;
  updatedAt?: string;
  category: string;
  tags: string[];
  thumbnail?: string;
  affiliateLinks?: AffiliateLink[];
  published: boolean;
}

export interface Post {
  slug: string;
  frontmatter: PostFrontmatter;
  content: string;
}

export interface AffiliateLink {
  label: string;
  url: string;
  provider: "amazon" | "rakuten" | "custom";
}

export interface SiteConfig {
  title: string;
  description: string;
  url: string;
  author: string;
  social: {
    twitter?: string;
    github?: string;
  };
  adsenseId?: string;
  gaId?: string;
}

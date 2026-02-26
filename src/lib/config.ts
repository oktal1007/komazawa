import { SiteConfig } from "@/types";

export const siteConfig: SiteConfig = {
  title: "Tech Insight",
  description:
    "テクノロジー・プログラミング・AI に関する最新情報と実践的なガイドをお届けするメディアサイト",
  url: process.env.NEXT_PUBLIC_SITE_URL || "https://example.com",
  author: "Tech Insight 編集部",
  social: {
    twitter: process.env.NEXT_PUBLIC_TWITTER_HANDLE || "",
    github: process.env.NEXT_PUBLIC_GITHUB_HANDLE || "",
  },
  adsenseId: process.env.NEXT_PUBLIC_ADSENSE_ID || "",
  gaId: process.env.NEXT_PUBLIC_GA_ID || "",
};

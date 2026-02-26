import Link from "next/link";
import { siteConfig } from "@/lib/config";

export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-gray-50">
      <div className="mx-auto max-w-5xl px-4 py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          <div>
            <h3 className="text-lg font-bold text-gray-900">
              {siteConfig.title}
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              {siteConfig.description}
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900">カテゴリ</h4>
            <ul className="mt-2 space-y-1">
              <li>
                <Link
                  href="/categories/プログラミング"
                  className="text-sm text-gray-600 hover:text-blue-600"
                >
                  プログラミング
                </Link>
              </li>
              <li>
                <Link
                  href="/categories/AI"
                  className="text-sm text-gray-600 hover:text-blue-600"
                >
                  AI
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900">リンク</h4>
            <ul className="mt-2 space-y-1">
              <li>
                <Link
                  href="/about"
                  className="text-sm text-gray-600 hover:text-blue-600"
                >
                  このサイトについて
                </Link>
              </li>
              <li>
                <Link
                  href="/privacy"
                  className="text-sm text-gray-600 hover:text-blue-600"
                >
                  プライバシーポリシー
                </Link>
              </li>
              <li>
                <a
                  href="/feed.xml"
                  className="text-sm text-gray-600 hover:text-blue-600"
                >
                  RSS
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-8 border-t border-gray-200 pt-8 text-center text-sm text-gray-500">
          &copy; {new Date().getFullYear()} {siteConfig.title}. All rights
          reserved.
        </div>
      </div>
    </footer>
  );
}

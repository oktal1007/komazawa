import { Metadata } from "next";
import { siteConfig } from "@/lib/config";

export const metadata: Metadata = {
  title: "プライバシーポリシー",
  description: `${siteConfig.title}のプライバシーポリシー`,
};

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="mb-8 text-3xl font-extrabold text-gray-900">
        プライバシーポリシー
      </h1>
      <div className="space-y-6 text-gray-700 leading-relaxed">
        <section>
          <h2 className="mb-3 text-xl font-bold text-gray-900">
            広告について
          </h2>
          <p>
            当サイトでは、Google
            AdSenseによる広告配信を行っております。Google及びそのパートナーは、Cookie
            を使用して、当サイトや他のサイトへの過去のアクセス情報に基づいて広告を配信します。
          </p>
          <p className="mt-2">
            ユーザーはGoogleの広告設定ページで、パーソナライズ広告を無効にできます。
          </p>
        </section>

        <section>
          <h2 className="mb-3 text-xl font-bold text-gray-900">
            アフィリエイトについて
          </h2>
          <p>
            当サイトは、Amazon.co.jpを宣伝しリンクすることによってサイトが紹介料を獲得できる手段を提供することを目的に設定されたアフィリエイトプログラムである、Amazonアソシエイト・プログラムの参加者です。
          </p>
        </section>

        <section>
          <h2 className="mb-3 text-xl font-bold text-gray-900">
            アクセス解析について
          </h2>
          <p>
            当サイトでは、Googleアナリティクスを使用してアクセス情報を収集しています。
            このデータは匿名で収集されており、個人を特定するものではありません。
          </p>
        </section>

        <section>
          <h2 className="mb-3 text-xl font-bold text-gray-900">免責事項</h2>
          <p>
            当サイトに掲載された内容によって生じた損害等の一切の責任を負いかねます。
            情報の正確性には十分に注意しておりますが、ご利用は自己責任でお願いいたします。
          </p>
        </section>
      </div>
    </div>
  );
}

import { Metadata } from "next";
import { siteConfig } from "@/lib/config";

export const metadata: Metadata = {
  title: "About",
  description: `${siteConfig.title}について`,
};

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="mb-8 text-3xl font-extrabold text-gray-900">
        このサイトについて
      </h1>
      <div className="space-y-6 text-gray-700 leading-relaxed">
        <p>
          {siteConfig.title}は、テクノロジー・プログラミング・AIに関する最新情報と
          実践的なガイドをお届けするメディアサイトです。
        </p>
        <h2 className="text-xl font-bold text-gray-900">運営者について</h2>
        <p>
          現役エンジニアが、日々の業務や学習で得た知識・経験を記事にまとめています。
          初心者から上級者まで、幅広い読者に役立つ情報を提供することを目指しています。
        </p>
        <h2 className="text-xl font-bold text-gray-900">お問い合わせ</h2>
        <p>
          記事に関するご質問やご意見は、各種SNSアカウントまたはメールにてお気軽にご連絡ください。
        </p>
      </div>
    </div>
  );
}

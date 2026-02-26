import { AffiliateLink } from "@/types";

interface AffiliateCardProps {
  links: AffiliateLink[];
}

const providerLabels: Record<AffiliateLink["provider"], string> = {
  amazon: "Amazon",
  rakuten: "楽天市場",
  custom: "詳細を見る",
};

const providerColors: Record<AffiliateLink["provider"], string> = {
  amazon: "bg-amber-500 hover:bg-amber-600",
  rakuten: "bg-red-500 hover:bg-red-600",
  custom: "bg-blue-500 hover:bg-blue-600",
};

export function AffiliateCard({ links }: AffiliateCardProps) {
  if (!links || links.length === 0) return null;

  return (
    <div className="my-8 rounded-xl border border-gray-200 bg-gray-50 p-6">
      <h3 className="mb-4 text-lg font-bold text-gray-800">
        おすすめの書籍・ツール
      </h3>
      <div className="space-y-3">
        {links.map((link, index) => (
          <div
            key={index}
            className="flex items-center justify-between rounded-lg bg-white p-4 shadow-sm"
          >
            <span className="font-medium text-gray-700">{link.label}</span>
            <a
              href={link.url}
              target="_blank"
              rel="noopener noreferrer sponsored"
              className={`rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors ${providerColors[link.provider]}`}
            >
              {providerLabels[link.provider]}で見る
            </a>
          </div>
        ))}
      </div>
      <p className="mt-3 text-xs text-gray-400">
        ※ 上記リンクはアフィリエイトリンクを含みます
      </p>
    </div>
  );
}

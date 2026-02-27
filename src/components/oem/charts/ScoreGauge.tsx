"use client";

interface ScoreGaugeProps {
  score: number;
  label: string;
  maxScore?: number;
}

export default function ScoreGauge({
  score,
  label,
  maxScore = 100,
}: ScoreGaugeProps) {
  const percentage = (score / maxScore) * 100;
  const color =
    percentage >= 70
      ? "text-green-600"
      : percentage >= 40
        ? "text-yellow-600"
        : "text-red-600";
  const bgColor =
    percentage >= 70
      ? "bg-green-500"
      : percentage >= 40
        ? "bg-yellow-500"
        : "bg-red-500";

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-24 h-24">
        <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
          <path
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke="#E5E7EB"
            strokeWidth="3"
          />
          <path
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeDasharray={`${percentage}, 100`}
            className={color}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-2xl font-bold ${color}`}>{score}</span>
        </div>
      </div>
      <div className="mt-2 flex items-center gap-1.5">
        <div className={`w-2 h-2 rounded-full ${bgColor}`} />
        <span className="text-sm text-gray-600">{label}</span>
      </div>
    </div>
  );
}

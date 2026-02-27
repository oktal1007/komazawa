const API_BASE = process.env.NEXT_PUBLIC_OEM_API_URL || "http://localhost:8000";

async function fetchAPI<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`API Error ${res.status}: ${error}`);
  }
  return res.json();
}

// Research
export async function searchMarket(keyword: string) {
  return fetchAPI<MarketSearchResult>("/api/research/search", {
    method: "POST",
    body: JSON.stringify({ keyword }),
  });
}

export async function getResearchHistory() {
  return fetchAPI<MarketResearchItem[]>("/api/research/history");
}

export async function getProductDetails(asin: string) {
  return fetchAPI<ProductDetails>(`/api/research/product/${asin}`);
}

// Review
export async function analyzeReviews(asin: string) {
  return fetchAPI<ReviewAnalysisResult>("/api/review/analyze", {
    method: "POST",
    body: JSON.stringify({ asin }),
  });
}

export async function getReviewHistory() {
  return fetchAPI<ReviewHistoryItem[]>("/api/review/history");
}

// Trends
export async function getIngredientTrends(weeks?: number) {
  const params = weeks ? `?weeks=${weeks}` : "";
  return fetchAPI<IngredientTrend[]>(`/api/trends/ingredients${params}`);
}

export async function getTrendReport() {
  return fetchAPI<TrendReport>("/api/trends/report");
}

// Factories
export interface FactoryFilters {
  category?: string;
  prefecture?: string;
  certification?: string;
  keyword?: string;
  favorite_only?: boolean;
}

export async function getFactories(filters?: FactoryFilters) {
  const params = new URLSearchParams();
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== "") {
        params.append(key, String(value));
      }
    });
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return fetchAPI<FactoryItem[]>(`/api/factories${query}`);
}

export async function toggleFactoryFavorite(id: number) {
  return fetchAPI<FactoryItem>(`/api/factories/${id}/favorite`, {
    method: "PUT",
  });
}

export async function updateFactoryMemo(id: number, memo: string) {
  return fetchAPI<FactoryItem>(`/api/factories/${id}/memo`, {
    method: "PUT",
    body: JSON.stringify({ memo }),
  });
}

export async function compareFactories(ids: number[]) {
  const params = ids.map((id) => `ids=${id}`).join("&");
  return fetchAPI<FactoryItem[]>(`/api/factories/compare?${params}`);
}

// Simulator
export async function calculateProfit(params: ProfitInput) {
  return fetchAPI<ProfitResult>("/api/simulator/calculate", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function saveSimulation(params: ProfitInput & ProfitResult) {
  return fetchAPI<{ id: number }>("/api/simulator/save", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function getSimulationHistory() {
  return fetchAPI<SimulationHistoryItem[]>("/api/simulator/history");
}

export async function deleteSimulation(id: number) {
  return fetchAPI<{ ok: boolean }>(`/api/simulator/${id}`, {
    method: "DELETE",
  });
}

// Types
export interface MarketResearchItem {
  id: number;
  keyword: string;
  asin: string;
  title: string;
  brand: string;
  price: number;
  review_count: number;
  rating: number;
  monthly_sales: number;
  monthly_revenue: number;
  market_score: number;
  created_at: string;
}

export interface MarketSearchResult {
  products: MarketResearchItem[];
  market_score: {
    total: number;
    market_size: number;
    competition: number;
    price_range: number;
    trend: number;
    new_entrant: number;
  };
  summary: {
    total_products: number;
    avg_price: number;
    median_price: number;
    min_price: number;
    max_price: number;
    avg_rating: number;
    total_monthly_revenue: number;
    fba_ratio: number;
    new_entrant_ratio: number;
  };
}

export interface ProductDetails {
  asin: string;
  title: string;
  brand: string;
  price: number;
  price_history: { date: string; price: number }[];
  rank_history: { date: string; rank: number }[];
  monthly_sales: number;
  annual_sales: number;
  fba_fee: number;
  buy_box_rate: number;
  seller_count: number;
}

export interface ReviewAnalysisResult {
  id: number;
  asin: string;
  negative_categories: { name: string; count: number }[];
  gap_analysis: string;
  differentiation_points: string[];
  strengths: string[];
  weaknesses: string[];
  winning_report: string;
  created_at: string;
}

export interface ReviewHistoryItem {
  id: number;
  asin: string;
  negative_summary: string;
  created_at: string;
}

export interface IngredientTrend {
  id: number;
  ingredient_name: string;
  mention_count: number;
  growth_rate: number;
  market_size: number;
  week_date: string;
}

export interface TrendReport {
  report: string;
  top_ingredients: string[];
  predictions: string[];
  generated_at: string;
}

export interface FactoryItem {
  id: number;
  name: string;
  prefecture: string;
  categories: string;
  dosage_forms: string;
  min_lot: number;
  url: string;
  contact_url: string;
  certifications: string;
  features: string;
  is_favorite: boolean;
  memo: string;
  created_at: string;
}

export interface ProfitInput {
  product_name: string;
  selling_price: number;
  manufacturing_cost: number;
  packaging_cost: number;
  fba_fee: number;
  ad_rate: number;
  target_sales: number;
}

export interface ProfitResult {
  profit_per_unit: number;
  profit_margin: number;
  monthly_profit: number;
  annual_profit: number;
  breakeven_units: number;
  roi: number;
  payback_months: number;
  scenarios: {
    optimistic: ScenarioResult;
    neutral: ScenarioResult;
    pessimistic: ScenarioResult;
  };
}

export interface ScenarioResult {
  target_sales: number;
  monthly_profit: number;
  annual_profit: number;
  roi: number;
}

export interface SimulationHistoryItem extends ProfitInput, ProfitResult {
  id: number;
  created_at: string;
}

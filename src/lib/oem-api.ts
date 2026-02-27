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

// ---- Research ----

interface BackendSearchResponse {
  keyword: string;
  total_products: number;
  market_score: number;
  market_summary: Record<string, { score: number; max: number; [k: string]: unknown }>;
  products: {
    asin: string;
    title: string;
    brand?: string;
    price?: number;
    review_count?: number;
    rating?: number;
    monthly_sales?: number;
    monthly_revenue?: number;
    market_score?: number;
  }[];
}

export async function searchMarket(keyword: string): Promise<MarketSearchResult> {
  const raw = await fetchAPI<BackendSearchResponse>("/api/research/search", {
    method: "POST",
    body: JSON.stringify({ keyword }),
  });

  const products: MarketResearchItem[] = raw.products.map((p, idx) => ({
    id: idx,
    keyword,
    asin: p.asin,
    title: p.title,
    brand: p.brand || "",
    price: p.price || 0,
    review_count: p.review_count || 0,
    rating: p.rating || 0,
    monthly_sales: p.monthly_sales || 0,
    monthly_revenue: p.monthly_revenue || 0,
    market_score: raw.market_score,
    created_at: new Date().toISOString(),
  }));

  const prices = products.map((p) => p.price).filter((p) => p > 0);
  const sortedPrices = [...prices].sort((a, b) => a - b);

  const factors = raw.market_summary || {};
  const getScore = (key: string) => {
    const f = factors[key];
    return f ? Math.round((f.score / f.max) * 100) : 50;
  };

  return {
    products,
    market_score: {
      total: Math.round(raw.market_score),
      market_size: getScore("market_size"),
      competition: getScore("competition"),
      price_range: getScore("price_range"),
      trend: getScore("trend"),
      new_entrant: getScore("new_entrant_success"),
    },
    summary: {
      total_products: raw.total_products,
      avg_price: prices.length ? Math.round(prices.reduce((a, b) => a + b, 0) / prices.length) : 0,
      median_price: sortedPrices.length ? sortedPrices[Math.floor(sortedPrices.length / 2)] : 0,
      min_price: sortedPrices.length ? sortedPrices[0] : 0,
      max_price: sortedPrices.length ? sortedPrices[sortedPrices.length - 1] : 0,
      avg_rating: products.length
        ? Math.round((products.reduce((a, p) => a + p.rating, 0) / products.length) * 10) / 10
        : 0,
      total_monthly_revenue: products.reduce((a, p) => a + p.monthly_revenue, 0),
      fba_ratio: 0.75,
      new_entrant_ratio: (factors.new_entrant_success as { ratio?: number } | undefined)?.ratio || 0.15,
    },
  };
}

interface BackendHistoryResponse {
  total: number;
  results: {
    keyword: string;
    market_score: number;
    created_at: string;
    product_count: number;
    products: {
      id: number;
      asin: string;
      title: string;
      brand?: string;
      price?: number;
      review_count?: number;
      rating?: number;
      monthly_sales?: number;
      monthly_revenue?: number;
    }[];
  }[];
}

export async function getResearchHistory(): Promise<MarketResearchItem[]> {
  const raw = await fetchAPI<BackendHistoryResponse>("/api/research/history");
  const items: MarketResearchItem[] = [];
  for (const group of raw.results) {
    for (const p of group.products) {
      items.push({
        id: p.id,
        keyword: group.keyword,
        asin: p.asin,
        title: p.title,
        brand: p.brand || "",
        price: p.price || 0,
        review_count: p.review_count || 0,
        rating: p.rating || 0,
        monthly_sales: p.monthly_sales || 0,
        monthly_revenue: p.monthly_revenue || 0,
        market_score: group.market_score,
        created_at: group.created_at,
      });
    }
  }
  return items;
}

export async function getProductDetails(asin: string): Promise<ProductDetails> {
  const raw = await fetchAPI<{
    asin: string;
    details: Record<string, unknown>;
    saved_data?: Record<string, unknown>;
  }>(`/api/research/product/${asin}`);

  const details = raw.details || {};
  return {
    asin: raw.asin,
    title: (details.title as string) || "",
    brand: (details.brand as string) || "",
    price: (details.price as number) || 0,
    price_history: (details.price_history as { date: string; price: number }[]) || [],
    rank_history: (details.rank_history as { date: string; rank: number }[]) || [],
    monthly_sales: (details.monthly_sales as number) || 0,
    annual_sales: (details.annual_sales as number) || 0,
    fba_fee: (details.fba_fee as number) || 0,
    buy_box_rate: (details.buy_box_rate as number) || 0,
    seller_count: (details.seller_count as number) || 0,
  };
}

// ---- Review ----

interface BackendReviewResponse {
  id?: number;
  asin: string;
  review_count: number;
  negative_categories: { category: string; count: number; severity: string; examples: string[] }[];
  gap_analysis: { gap: string; frequency: string; opportunity: string }[];
  differentiation_points: { point: string; description: string; priority: string }[];
  strengths: { strength: string; mention_count: number }[];
  weaknesses: { weakness: string; mention_count: number; improvement_suggestion: string }[];
  overall_sentiment: { positive_ratio: number; neutral_ratio: number; negative_ratio: number; summary: string };
  created_at?: string;
}

export async function analyzeReviews(asin: string): Promise<ReviewAnalysisResult> {
  const raw = await fetchAPI<BackendReviewResponse>("/api/review/analyze", {
    method: "POST",
    body: JSON.stringify({ asin }),
  });

  return {
    id: raw.id || 0,
    asin: raw.asin,
    negative_categories: raw.negative_categories.map((c) => ({
      name: c.category,
      count: c.count,
    })),
    gap_analysis: raw.gap_analysis.map((g) => `${g.gap}: ${g.opportunity}`).join("\n\n"),
    differentiation_points: raw.differentiation_points.map((d) => `${d.point}: ${d.description}`),
    strengths: raw.strengths.map((s) => s.strength),
    weaknesses: raw.weaknesses.map((w) => `${w.weakness} → ${w.improvement_suggestion}`),
    winning_report: raw.overall_sentiment.summary || "",
    created_at: raw.created_at || new Date().toISOString(),
  };
}

export async function getReviewHistory(): Promise<ReviewHistoryItem[]> {
  const raw = await fetchAPI<{
    total: number;
    results: { id: number; asin: string; created_at: string; summary?: string }[];
  }>("/api/review/history");
  return raw.results.map((r) => ({
    id: r.id,
    asin: r.asin,
    negative_summary: r.summary || "",
    created_at: r.created_at,
  }));
}

// ---- Trends ----

interface BackendTrendsResponse {
  weeks: number;
  total_ingredients: number;
  trends: {
    ingredient_name: string;
    latest_mention_count?: number;
    avg_growth_rate?: number;
    latest_market_size?: number;
    trend_direction: string;
    data_points: {
      id: number;
      mention_count?: number;
      growth_rate?: number;
      market_size?: number;
      week_date?: string;
    }[];
  }[];
}

export async function getIngredientTrends(weeks?: number): Promise<IngredientTrend[]> {
  const params = weeks ? `?weeks=${weeks}` : "";
  const raw = await fetchAPI<BackendTrendsResponse>(`/api/trends/ingredients${params}`);

  const items: IngredientTrend[] = [];
  for (const trend of raw.trends) {
    for (const dp of trend.data_points) {
      items.push({
        id: dp.id,
        ingredient_name: trend.ingredient_name,
        mention_count: dp.mention_count || 0,
        growth_rate: (dp.growth_rate || 0) / 100,
        market_size: (dp.market_size || 0) * 100000000,
        week_date: dp.week_date || "",
      });
    }
  }
  return items;
}

export async function getTrendReport(): Promise<TrendReport> {
  const raw = await fetchAPI<{
    report: {
      report: string;
      top_ingredients: string[];
      predictions: string[];
      generated_at: string;
    };
    data_points_analyzed: number;
  }>("/api/trends/report");

  return {
    report: raw.report.report,
    top_ingredients: raw.report.top_ingredients,
    predictions: raw.report.predictions,
    generated_at: raw.report.generated_at,
  };
}

// ---- Factories ----

export interface FactoryFilters {
  category?: string;
  prefecture?: string;
  certification?: string;
  keyword?: string;
  favorite_only?: boolean;
}

interface BackendFactoryItem {
  id: number;
  name: string;
  prefecture?: string;
  categories?: string[] | null;
  dosage_forms?: string[] | null;
  min_lot?: string | null;
  url?: string;
  contact_url?: string;
  certifications?: string[] | null;
  features?: string;
  is_favorite: boolean;
  memo?: string;
  created_at: string;
}

function backendFactoryToFrontend(f: BackendFactoryItem): FactoryItem {
  return {
    id: f.id,
    name: f.name,
    prefecture: f.prefecture || "",
    categories: Array.isArray(f.categories) ? f.categories.join(",") : (f.categories || ""),
    dosage_forms: Array.isArray(f.dosage_forms) ? f.dosage_forms.join(",") : (f.dosage_forms || ""),
    min_lot: typeof f.min_lot === "string" ? parseInt(f.min_lot.replace(/[^0-9]/g, ""), 10) || 0 : (f.min_lot || 0),
    url: f.url || "",
    contact_url: f.contact_url || "",
    certifications: Array.isArray(f.certifications) ? f.certifications.join(",") : (f.certifications || ""),
    features: f.features || "",
    is_favorite: f.is_favorite,
    memo: f.memo || "",
    created_at: f.created_at,
  };
}

export async function getFactories(filters?: FactoryFilters): Promise<FactoryItem[]> {
  const params = new URLSearchParams();
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== "") {
        params.append(key, String(value));
      }
    });
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  const raw = await fetchAPI<{ total: number; factories: BackendFactoryItem[] }>(
    `/api/factories${query}`
  );
  return raw.factories.map(backendFactoryToFrontend);
}

export async function toggleFactoryFavorite(id: number): Promise<FactoryItem> {
  // First get current state, then toggle
  const current = await fetchAPI<BackendFactoryItem>(`/api/factories/${id}`);
  const raw = await fetchAPI<BackendFactoryItem>(`/api/factories/${id}/favorite`, {
    method: "PUT",
    body: JSON.stringify({ is_favorite: !current.is_favorite }),
  });
  return backendFactoryToFrontend(raw);
}

export async function updateFactoryMemo(id: number, memo: string): Promise<FactoryItem> {
  const raw = await fetchAPI<BackendFactoryItem>(`/api/factories/${id}/memo`, {
    method: "PUT",
    body: JSON.stringify({ memo }),
  });
  return backendFactoryToFrontend(raw);
}

export async function compareFactories(ids: number[]): Promise<FactoryItem[]> {
  const idsParam = ids.join(",");
  const raw = await fetchAPI<{ factories: BackendFactoryItem[]; comparison_summary: unknown }>(
    `/api/factories/compare?ids=${idsParam}`
  );
  return raw.factories.map(backendFactoryToFrontend);
}

// ---- Simulator ----

interface BackendCalculateResponse {
  selling_price: number;
  manufacturing_cost: number;
  packaging_cost: number;
  fba_fee: number;
  referral_fee: number;
  ad_cost_per_unit: number;
  total_cost_per_unit: number;
  profit_per_unit: number;
  profit_margin: number;
  monthly_revenue: number;
  monthly_profit: number;
  annual_revenue: number;
  annual_profit: number;
  breakeven_units: number;
  initial_investment: number;
  roi: number;
  payback_months: number | null;
  target_sales: number;
  ad_rate: number;
  cost_breakdown: Record<string, number>;
  fba_fee_detail?: Record<string, unknown>;
  scenarios?: Record<string, {
    label: string;
    multiplier: number;
    profit_per_unit: number;
    profit_margin: number;
    monthly_profit: number;
    annual_profit: number;
    target_sales: number;
    roi: number;
    [k: string]: unknown;
  }>;
}

export async function calculateProfit(params: ProfitInput): Promise<ProfitResult> {
  const raw = await fetchAPI<BackendCalculateResponse>("/api/simulator/calculate", {
    method: "POST",
    body: JSON.stringify(params),
  });

  const scenarios = raw.scenarios || {};
  return {
    profit_per_unit: raw.profit_per_unit,
    profit_margin: raw.profit_margin / 100,
    monthly_profit: raw.monthly_profit,
    annual_profit: raw.annual_profit,
    breakeven_units: raw.breakeven_units,
    roi: raw.roi / 100,
    payback_months: raw.payback_months || 999,
    scenarios: {
      optimistic: {
        target_sales: scenarios.optimistic?.target_sales || 0,
        monthly_profit: scenarios.optimistic?.monthly_profit || 0,
        annual_profit: scenarios.optimistic?.annual_profit || 0,
        roi: (scenarios.optimistic?.roi || 0) / 100,
      },
      neutral: {
        target_sales: scenarios.neutral?.target_sales || 0,
        monthly_profit: scenarios.neutral?.monthly_profit || 0,
        annual_profit: scenarios.neutral?.annual_profit || 0,
        roi: (scenarios.neutral?.roi || 0) / 100,
      },
      pessimistic: {
        target_sales: scenarios.pessimistic?.target_sales || 0,
        monthly_profit: scenarios.pessimistic?.monthly_profit || 0,
        annual_profit: scenarios.pessimistic?.annual_profit || 0,
        roi: (scenarios.pessimistic?.roi || 0) / 100,
      },
    },
  };
}

export async function saveSimulation(params: ProfitInput & ProfitResult): Promise<{ id: number }> {
  const raw = await fetchAPI<{ id: number; message: string }>("/api/simulator/save", {
    method: "POST",
    body: JSON.stringify({
      product_name: params.product_name,
      selling_price: params.selling_price,
      manufacturing_cost: params.manufacturing_cost,
      packaging_cost: params.packaging_cost,
      fba_fee: params.fba_fee,
      ad_rate: params.ad_rate,
      target_sales: params.target_sales,
    }),
  });
  return { id: raw.id };
}

export async function getSimulationHistory(): Promise<SimulationHistoryItem[]> {
  const raw = await fetchAPI<{
    total: number;
    simulations: {
      id: number;
      product_name: string;
      selling_price: number;
      manufacturing_cost: number;
      packaging_cost: number;
      fba_fee: number;
      ad_rate: number;
      target_sales: number;
      profit_per_unit?: number;
      profit_margin?: number;
      monthly_profit?: number;
      roi?: number;
      created_at: string;
    }[];
  }>("/api/simulator/history");

  return raw.simulations.map((s) => ({
    id: s.id,
    product_name: s.product_name,
    selling_price: s.selling_price,
    manufacturing_cost: s.manufacturing_cost,
    packaging_cost: s.packaging_cost,
    fba_fee: s.fba_fee,
    ad_rate: s.ad_rate,
    target_sales: s.target_sales,
    profit_per_unit: s.profit_per_unit || 0,
    profit_margin: (s.profit_margin || 0) / 100,
    monthly_profit: s.monthly_profit || 0,
    annual_profit: (s.monthly_profit || 0) * 12,
    breakeven_units: 0,
    roi: (s.roi || 0) / 100,
    payback_months: 0,
    scenarios: {
      optimistic: { target_sales: 0, monthly_profit: 0, annual_profit: 0, roi: 0 },
      neutral: { target_sales: 0, monthly_profit: 0, annual_profit: 0, roi: 0 },
      pessimistic: { target_sales: 0, monthly_profit: 0, annual_profit: 0, roi: 0 },
    },
    created_at: s.created_at,
  }));
}

export async function deleteSimulation(id: number): Promise<{ ok: boolean }> {
  await fetchAPI<{ status: string; message: string }>(`/api/simulator/${id}`, {
    method: "DELETE",
  });
  return { ok: true };
}

// ---- Types (used by frontend pages) ----

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

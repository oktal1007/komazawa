"""バステト神AI占い鑑定レポート自動生成 - FastAPI Backend"""

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.numerology import calculate_numerology
from services.astrology import calculate_astrology
from services.four_pillars import calculate_four_pillars
from services.divination_generator import generate_divination_report
from services.canva_exporter import CanvaExporter

load_dotenv()

app = FastAPI(
    title="バステト神AI占い鑑定レポート自動生成API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- リクエスト/レスポンスモデル ---


class DivinationRequest(BaseModel):
    customer_name: str = Field(..., description="お客様名（フルネーム）")
    birth_year: int = Field(..., ge=1900, le=2100, description="生年（西暦）")
    birth_month: int = Field(..., ge=1, le=12, description="生月")
    birth_day: int = Field(..., ge=1, le=31, description="生日")
    birth_hour: Optional[int] = Field(None, ge=0, le=23, description="出生時刻（時）")
    gender: str = Field(..., description="性別")
    category: str = Field(..., description="鑑定カテゴリ（恋愛/仕事/金運/総合運）")
    menu_name: str = Field(..., description="鑑定メニュー名")
    consultation_content: str = Field(..., description="お客様の相談内容")
    additional_memo: str = Field("", description="追加メモ")
    divination_methods: list[str] = Field(
        ..., description="使用占術（数秘術/西洋占星術/四柱推命）"
    )


class CalculationResponse(BaseModel):
    numerology: Optional[dict] = None
    astrology: Optional[dict] = None
    four_pillars: Optional[dict] = None


class GenerateReportResponse(BaseModel):
    generated_content: dict
    calculations: dict


class ExportPdfResponse(BaseModel):
    design_id: str
    export_url: str


# --- APIエンドポイント ---


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "bastet-divination-api"}


@app.post("/api/calculate", response_model=CalculationResponse)
async def calculate_divination(req: DivinationRequest):
    """占術の自動計算を実行"""
    result = CalculationResponse()

    if "数秘術" in req.divination_methods or "フルパッケージ" in req.divination_methods:
        result.numerology = calculate_numerology(
            req.customer_name, req.birth_year, req.birth_month, req.birth_day
        )

    if "西洋占星術" in req.divination_methods or "フルパッケージ" in req.divination_methods:
        birth_hour_float = float(req.birth_hour) if req.birth_hour is not None else None
        result.astrology = calculate_astrology(
            req.birth_year, req.birth_month, req.birth_day, birth_hour_float
        )

    if "四柱推命" in req.divination_methods or "フルパッケージ" in req.divination_methods:
        result.four_pillars = calculate_four_pillars(
            req.birth_year, req.birth_month, req.birth_day, req.birth_hour
        )

    return result


@app.post("/api/generate", response_model=GenerateReportResponse)
async def generate_report(req: DivinationRequest):
    """占術計算 + Claude API鑑定文生成"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY is not set")

    # 占術計算
    calc_result = await calculate_divination(req)

    # 鑑定文生成
    generated = await generate_divination_report(
        api_key=api_key,
        customer_name=req.customer_name,
        category=req.category,
        menu_name=req.menu_name,
        consultation_content=req.consultation_content,
        divination_methods=req.divination_methods,
        numerology_result=calc_result.numerology,
        astrology_result=calc_result.astrology,
        four_pillars_result=calc_result.four_pillars,
        additional_memo=req.additional_memo,
    )

    return GenerateReportResponse(
        generated_content=generated,
        calculations=calc_result.model_dump(),
    )


@app.post("/api/export-pdf", response_model=ExportPdfResponse)
async def export_pdf(generated_content: dict):
    """Canva APIでPDFエクスポート"""
    canva_token = os.getenv("CANVA_ACCESS_TOKEN")
    if not canva_token:
        raise HTTPException(status_code=500, detail="CANVA_ACCESS_TOKEN is not set")

    exporter = CanvaExporter(canva_token)
    result = await exporter.generate_pdf(generated_content)
    return ExportPdfResponse(**result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

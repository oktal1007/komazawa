"""バステト神AI占い鑑定レポート自動生成 - FastAPI Backend"""

import os
from typing import Optional

from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.numerology import calculate_numerology
from services.astrology import calculate_astrology
from services.four_pillars import calculate_four_pillars
from services.divination_generator import generate_divination_report
from services.canva_exporter import CanvaExporter
from services.canva_oauth import CanvaOAuth

load_dotenv()

# Canva OAuthインスタンス（グローバル）
_canva_oauth: CanvaOAuth | None = None


def get_canva_oauth() -> CanvaOAuth:
    global _canva_oauth
    if _canva_oauth is None:
        client_id = os.getenv("CANVA_CLIENT_ID", "")
        client_secret = os.getenv("CANVA_CLIENT_SECRET", "")
        redirect_uri = os.getenv("CANVA_REDIRECT_URI", "http://127.0.0.1:8000/api/canva/callback")
        if not client_id or not client_secret:
            raise RuntimeError("CANVA_CLIENT_ID / CANVA_CLIENT_SECRET が未設定です")
        _canva_oauth = CanvaOAuth(client_id, client_secret, redirect_uri)
    return _canva_oauth

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
    oauth = get_canva_oauth()
    canva_token = await oauth.get_valid_access_token()
    if not canva_token:
        raise HTTPException(
            status_code=401,
            detail="Canva未認証です。先に /api/canva/authorize で認証してください",
        )

    exporter = CanvaExporter(canva_token)
    result = await exporter.generate_pdf(generated_content)
    return ExportPdfResponse(**result)


# --- Canva OAuth エンドポイント ---


@app.get("/api/canva/authorize")
async def canva_authorize():
    """Canva OAuth認可URLを生成して返す"""
    oauth = get_canva_oauth()
    return oauth.get_authorization_url()


@app.get("/api/canva/callback")
async def canva_callback(code: str = "", state: str = "", error: str = ""):
    """Canva OAuthコールバック。認可コードをトークンに交換"""
    if error:
        raise HTTPException(status_code=400, detail=f"Canva authorization error: {error}")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")

    oauth = get_canva_oauth()
    try:
        token_data = await oauth.exchange_code(code, state)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Token exchange failed: {e.response.text}")

    return {
        "status": "success",
        "message": "Canva認証が完了しました。このページを閉じてください。",
        "expires_in": token_data.get("expires_in"),
    }


@app.get("/api/canva/status")
async def canva_status():
    """Canva認証状態を確認"""
    oauth = get_canva_oauth()
    token = await oauth.get_valid_access_token()
    return {
        "authenticated": token is not None,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

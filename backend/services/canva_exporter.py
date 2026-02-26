"""Canva API連携サービス - テンプレートからPDF生成"""

import asyncio
import time
from typing import Optional

import httpx

CANVA_API_BASE = "https://api.canva.com/rest/v1"
TEMPLATE_DESIGN_ID = "DAG6v4MOJZ8"

# テキスト要素ID
ELEMENT_IDS = {
    "p1_title": "PBx2BHqMdxJNYGVP-LBbBrHppq9mszHmg",
    "p1_body": "PBx2BHqMdxJNYGVP-LB8m5N4GQ9blRpg9",
    "p2_body": "PBgC1zdZRkBJfKS7-LB3H1nylMY8VYplS",
    "p3_body": "PBK1qmHJX42BVY9N-LB6gxw9RKzsJHJCh",
}


class CanvaExporter:
    """Canva APIを使ってテンプレートからPDFを生成"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self, method: str, path: str, json_data: Optional[dict] = None
    ) -> dict:
        """Canva APIにリクエストを送信"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method,
                f"{CANVA_API_BASE}{path}",
                headers=self.headers,
                json=json_data,
            )
            response.raise_for_status()
            return response.json()

    async def copy_template(self, title: str) -> str:
        """テンプレートをコピーして新規デザインを作成。デザインIDを返す"""
        result = await self._request(
            "POST",
            "/designs",
            {
                "design_type": {"type": "preset", "name": "doc"},
                "title": title,
                "asset_id": TEMPLATE_DESIGN_ID,
            },
        )
        return result["design"]["id"]

    async def start_edit_transaction(self, design_id: str) -> str:
        """編集トランザクションを開始"""
        result = await self._request(
            "POST",
            f"/designs/{design_id}/editing/transactions",
        )
        return result["transaction"]["id"]

    async def perform_edit_operations(
        self,
        design_id: str,
        transaction_id: str,
        operations: list[dict],
    ) -> dict:
        """編集オペレーションを実行"""
        return await self._request(
            "POST",
            f"/designs/{design_id}/editing/transactions/{transaction_id}/operations",
            {"operations": operations},
        )

    async def duplicate_page(
        self,
        design_id: str,
        transaction_id: str,
        source_page_index: int,
        target_page_index: int,
    ) -> dict:
        """ページを複製"""
        return await self.perform_edit_operations(
            design_id,
            transaction_id,
            [
                {
                    "type": "duplicate_page",
                    "source_page_index": source_page_index,
                    "target_page_index": target_page_index,
                }
            ],
        )

    async def commit_transaction(self, design_id: str, transaction_id: str) -> dict:
        """トランザクションをコミット"""
        return await self._request(
            "POST",
            f"/designs/{design_id}/editing/transactions/{transaction_id}/commit",
        )

    async def export_design(self, design_id: str) -> str:
        """デザインをPDFとしてエクスポート。ダウンロードURLを返す"""
        result = await self._request(
            "POST",
            "/exports",
            {
                "design_id": design_id,
                "format": {"type": "pdf"},
                "quality": "pro",
            },
        )
        job_id = result["job"]["id"]

        # エクスポート完了をポーリング
        for _ in range(30):
            status = await self._request("GET", f"/exports/{job_id}")
            if status["job"]["status"] == "success":
                return status["job"]["result"]["url"]
            if status["job"]["status"] == "failed":
                raise RuntimeError(f"Export failed: {status}")
            await asyncio.sleep(2)

        raise TimeoutError("Export timed out")

    async def generate_pdf(self, generated_content: dict) -> dict:
        """鑑定レポートのPDFを生成

        Args:
            generated_content: Claude APIが生成した鑑定レポート
                {
                    "title": "バステト女神からの...",
                    "pages": [
                        {"page_role": "cover", "text": "..."},
                        {"page_role": "body", "text": "..."},
                        {"page_role": "closing", "text": "..."},
                    ]
                }

        Returns:
            {"design_id": "...", "export_url": "..."}
        """
        title = generated_content["title"]
        pages = generated_content["pages"]

        # Step1: テンプレートをコピー
        design_id = await self.copy_template(title)

        # Step2: 編集トランザクション開始
        transaction_id = await self.start_edit_transaction(design_id)

        # Step3: ページ構成を解析
        cover_page = pages[0]
        body_pages = [p for p in pages[1:] if p["page_role"] == "body"]
        closing_page = pages[-1]

        # Step4: P1（表紙）のタイトルと本文を差し替え
        await self.perform_edit_operations(
            design_id,
            transaction_id,
            [
                {
                    "type": "replace_text",
                    "element_id": ELEMENT_IDS["p1_title"],
                    "text": title,
                },
                {
                    "type": "replace_text",
                    "element_id": ELEMENT_IDS["p1_body"],
                    "text": cover_page["text"],
                },
            ],
        )

        # Step5: P2（最初のbody）の本文を差し替え
        if body_pages:
            await self.perform_edit_operations(
                design_id,
                transaction_id,
                [
                    {
                        "type": "replace_text",
                        "element_id": ELEMENT_IDS["p2_body"],
                        "text": body_pages[0]["text"],
                    },
                ],
            )

        # Step6: 追加bodyページがある場合はP2レイアウトを複製して追加
        # テンプレートのP2はindex=1。追加ページはP2の後ろに挿入
        for i, extra_body in enumerate(body_pages[1:], start=1):
            # P2(index=1)を複製して、index=1+i の位置に挿入
            dup_result = await self.duplicate_page(
                design_id, transaction_id,
                source_page_index=1,
                target_page_index=1 + i,
            )
            # 複製されたページのテキスト要素に本文をセット
            # 複製ページは元ページと同じelement_idを持つ場合、
            # ページ固有の新しいelement_idが割り振られる可能性がある
            # その場合はdup_resultからelement_idを取得する必要がある
            if "page" in dup_result and "elements" in dup_result["page"]:
                # 新ページのテキスト要素を検索
                for elem in dup_result["page"]["elements"]:
                    if elem.get("type") == "text":
                        await self.perform_edit_operations(
                            design_id,
                            transaction_id,
                            [
                                {
                                    "type": "replace_text",
                                    "element_id": elem["id"],
                                    "text": extra_body["text"],
                                }
                            ],
                        )
                        break

        # Step7: P3（closing）の本文を差し替え
        await self.perform_edit_operations(
            design_id,
            transaction_id,
            [
                {
                    "type": "replace_text",
                    "element_id": ELEMENT_IDS["p3_body"],
                    "text": closing_page["text"],
                },
            ],
        )

        # Step8: コミット
        await self.commit_transaction(design_id, transaction_id)

        # Step9: PDFエクスポート
        export_url = await self.export_design(design_id)

        return {
            "design_id": design_id,
            "export_url": export_url,
        }

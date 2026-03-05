import { NextResponse } from "next/server";

const API_BASE = process.env.BACKEND_API_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${API_BASE}/api/canva/authorize`);
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { detail: error instanceof Error ? error.message : "Failed to get authorization URL" },
      { status: 500 }
    );
  }
}

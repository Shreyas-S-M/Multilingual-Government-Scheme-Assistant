import { NextRequest, NextResponse } from "next/server";

const BACKEND = (process.env.BACKEND_API_URL || "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json().catch(() => ({}));
    const upstream = await fetch(`${BACKEND}/chat/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    const data = await upstream.json().catch(() => ({ detail: "Unreadable reset response" }));
    return NextResponse.json(data, { status: upstream.status });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown connection error";
    return NextResponse.json(
      { detail: `Could not reset session on backend: ${message}` },
      { status: 502 }
    );
  }
}


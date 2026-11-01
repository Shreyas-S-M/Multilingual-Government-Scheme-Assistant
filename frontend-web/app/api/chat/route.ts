import { NextRequest, NextResponse } from "next/server";

const BACKEND = (process.env.BACKEND_API_URL || "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json();
    const upstream = await fetch(`${BACKEND}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
      signal: AbortSignal.timeout(65000),
    });
    const data = await upstream.json().catch(() => ({ detail: "The API returned an unreadable response." }));
    return NextResponse.json(data, { status: upstream.status });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown connection error";
    return NextResponse.json({ detail: `Could not reach the FastAPI backend. Check that it is running on port 8000. (${message})` }, { status: 502 });
  }
}

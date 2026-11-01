import { NextResponse } from "next/server";
const BACKEND = (process.env.BACKEND_API_URL || "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");
export async function GET() {
  try {
    const response = await fetch(`${BACKEND}/health`, { cache: "no-store", signal: AbortSignal.timeout(5000) });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ status: "unreachable" }, { status: 503 });
  }
}

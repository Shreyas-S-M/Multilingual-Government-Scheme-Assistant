import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { getSupabaseConfig } from "./config";

export async function updateSession(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Immediately allow internal Next.js routes, static assets, and dev helpers to pass through
  if (
    pathname.startsWith("/_") ||
    pathname === "/favicon.ico" ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  let supabaseResponse = NextResponse.next({
    request,
  });

  const { url, key } = getSupabaseConfig();

  const supabase = createServerClient(url, key, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
        supabaseResponse = NextResponse.next({
          request,
        });
        cookiesToSet.forEach(({ name, value, options }) =>
          supabaseResponse.cookies.set(name, value, options)
        );
      },
    },
  });

  // IMPORTANT: Use getUser() to securely revalidate user credentials with Supabase Auth
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Public paths accessible without authentication
  const isPublicAuthPath =
    pathname.startsWith("/login") ||
    pathname.startsWith("/auth") ||
    pathname.startsWith("/reset-password") ||
    pathname.startsWith("/api/health");

  // If user is NOT authenticated and trying to access any protected page or chat API:
  if (!user && !isPublicAuthPath) {
    if (pathname.startsWith("/api/")) {
      return NextResponse.json(
        { error: "Authentication required to access Sahayaka assistant." },
        { status: 401 }
      );
    }
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = "/login";
    if (pathname !== "/") {
      redirectUrl.searchParams.set("redirectTo", pathname);
    }
    return NextResponse.redirect(redirectUrl);
  }

  // Redirect authenticated users away from the login/signup page
  if (user && pathname === "/login") {
    const redirectTo = request.nextUrl.searchParams.get("redirectTo") || "/";
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = redirectTo;
    redirectUrl.searchParams.delete("redirectTo");
    return NextResponse.redirect(redirectUrl);
  }

  return supabaseResponse;
}


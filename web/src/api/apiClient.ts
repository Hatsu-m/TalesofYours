import type { paths } from './types';

const BASE_URL = import.meta.env.VITE_API_URL ?? '';

type Path = keyof paths;

type Method<P extends Path> = keyof paths[P];

type RequestBody<P extends Path, M extends Method<P>> =
  paths[P][M] extends { requestBody: { content: { 'application/json': infer B } } }
    ? B
    : never;

type ResponseBody<P extends Path, M extends Method<P>> =
  paths[P][M] extends { responses: { 200: { content: { 'application/json': infer R } } } }
    ? R
    : never;

export async function apiClient<P extends Path, M extends Method<P>>(
  path: P,
  method: M,
  body?: RequestBody<P, M>,
): Promise<ResponseBody<P, M>> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: method.toUpperCase(),
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    throw new Error(`Request failed with status ${res.status}`);
  }

  return (await res.json()) as ResponseBody<P, M>;
}

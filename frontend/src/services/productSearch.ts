import type { SearchResponse } from '../types/product'

interface ValidationError {
  msg?: string
}

interface ErrorResponse {
  detail?: string | ValidationError[]
}

function getErrorMessage(body: ErrorResponse): string {
  if (typeof body.detail === 'string') {
    return body.detail
  }

  if (Array.isArray(body.detail)) {
    return body.detail
      .map((error) => error.msg)
      .filter(Boolean)
      .join('. ')
  }

  return 'No fue posible realizar la búsqueda.'
}

export async function searchProducts(
  query: string,
  limit = 20,
): Promise<SearchResponse> {
  const parameters = new URLSearchParams({
    q: query,
    limit: String(limit),
    providers: 'demo_store',
  })

  const response = await fetch(
    `/api/v1/search?${parameters.toString()}`,
  )

  if (!response.ok) {
    const body = (await response.json()) as ErrorResponse

    throw new Error(getErrorMessage(body))
  }

  return (await response.json()) as SearchResponse
}
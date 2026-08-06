export interface Product {
  id: string
  nombre: string
  precio: number
  precio_original: number | null
  moneda: string
  tienda: string
  url: string
  imagen_url: string | null
  condicion: string | null
  envio_gratis: boolean
  calificacion: number | null
  numero_resenas: number
}

export interface SearchResponse {
  query: string
  total: number
  source: string
  fallback_used: boolean
  warning: string | null
  products: Product[]
}
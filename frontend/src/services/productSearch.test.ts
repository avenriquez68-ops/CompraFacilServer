import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest'

import { searchProducts } from './productSearch'
import type { SearchResponse } from '../types/product'

const successfulResponse: SearchResponse = {
  query: 'laptop',
  total: 1,
  source: 'multi_provider',
  fallback_used: false,
  warning: null,
  products: [
    {
      id: 'MLM123',
      nombre: 'Laptop de Mercado Libre',
      precio: 12999,
      precio_original: null,
      moneda: 'MXN',
      tienda: 'Mercado Libre',
      url: 'https://example.com/producto',
      imagen_url: null,
      condicion: 'nuevo',
      envio_gratis: true,
      calificacion: 4.5,
      numero_resenas: 10,
    },
  ],
}

describe('searchProducts', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it('consulta el endpoint con los parámetros esperados', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(successfulResponse),
    })

    vi.stubGlobal('fetch', fetchMock)

    const result = await searchProducts('laptop', 5)

    expect(fetchMock).toHaveBeenCalledOnce()
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/search?q=laptop&limit=5&providers=mercado_libre',
    )
    expect(result).toEqual(successfulResponse)
  })

  it('usa la API pública configurada', async () => {
    vi.stubEnv(
      'VITE_API_BASE_URL',
      'https://api.dameprecio.shop',
    )

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(successfulResponse),
    })

    vi.stubGlobal('fetch', fetchMock)

    await searchProducts('celular', 10)

    expect(fetchMock).toHaveBeenCalledWith(
      (
        'https://api.dameprecio.shop'
        + '/api/v1/search'
        + '?q=celular&limit=10'
        + '&providers=mercado_libre'
      ),
    )
  })

  it('devuelve el mensaje enviado por el servidor', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        json: vi.fn().mockResolvedValue({
          detail: 'Proveedor no disponible.',
        }),
      }),
    )

    await expect(
      searchProducts('laptop'),
    ).rejects.toThrow('Proveedor no disponible.')
  })

  it('convierte los errores de validación en un mensaje', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        json: vi.fn().mockResolvedValue({
          detail: [
            {
              msg: 'La búsqueda es demasiado corta.',
            },
          ],
        }),
      }),
    )

    await expect(
      searchProducts('a'),
    ).rejects.toThrow(
      'La búsqueda es demasiado corta.',
    )
  })
})
import { useState, type FormEvent } from 'react'
import { searchProducts } from './services/productSearch'
import type {
  Product,
  SearchResponse,
} from './types/product'
import './App.css'

function formatPrice(product: Product): string {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: product.moneda,
  }).format(product.precio)
}

function getProviderId(store: string): string | null {
  const normalizedStore = store.toLowerCase()

  if (normalizedStore.includes('mercado libre')) {
    return 'mercado_libre'
  }

  if (normalizedStore.includes('demo')) {
    return 'demo_store'
  }

  return null
}

function getProductUrl(product: Product): string {
  const providerId = getProviderId(product.tienda)

  if (!providerId) {
    return product.url
  }

  const parameters = new URLSearchParams({
    provider_id: providerId,
    product_url: product.url,
  })

  return `/api/v1/redirect?${parameters.toString()}`
}

function ProductCard({ product }: { product: Product }) {
  return (
    <article className="product-card">
      <div className="product-image">
        {product.imagen_url ? (
          <img
            src={product.imagen_url}
            alt={product.nombre}
            loading="lazy"
          />
        ) : (
          <span>Sin imagen</span>
        )}
      </div>

      <div className="product-information">
        <span className="store-name">{product.tienda}</span>

        <h3>{product.nombre}</h3>

        <div className="price-row">
          <strong>{formatPrice(product)}</strong>

          {product.precio_original &&
            product.precio_original > product.precio && (
              <del>
                {new Intl.NumberFormat('es-MX', {
                  style: 'currency',
                  currency: product.moneda,
                }).format(product.precio_original)}
              </del>
            )}
        </div>

        <div className="product-details">
          {product.envio_gratis && (
            <span className="free-shipping">Envío gratis</span>
          )}

          {product.condicion && (
            <span>{product.condicion}</span>
          )}

          {product.calificacion !== null && (
            <span>
              ★ {product.calificacion.toFixed(1)}
              {product.numero_resenas > 0 &&
                ` (${product.numero_resenas})`}
            </span>
          )}
        </div>

        <a
          className="product-link"
          href={getProductUrl(product)}
          target="_blank"
          rel="noopener noreferrer sponsored"
        >
          Ver en la tienda
        </a>
      </div>
    </article>
  )
}

function App() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const normalizedQuery = query.trim()

    if (normalizedQuery.length < 2) {
      setError('Escribe al menos dos caracteres.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const searchResult = await searchProducts(normalizedQuery)
      setResult(searchResult)
    } catch (searchError) {
      setResult(null)

      setError(
        searchError instanceof Error
          ? searchError.message
          : 'Ocurrió un error inesperado.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <a className="brand" href="/" aria-label="Dame Precio">
          <img
            className="brand-logo"
            src="/dameprecio-logo.png"
            alt="Dame Precio"
          />
        </a>

        <span className="project-status">
          Proyecto mexicano
        </span>
      </header>

      <main>
        <section className="hero">
          <span className="eyebrow">
            Compara antes de comprar
          </span>

          <h1>
            Encuentra una mejor opción
            <span> sin abrir tantas pestañas.</span>
          </h1>

          <p className="hero-description">
            Busca productos y compara información disponible de
            distintas tiendas desde un solo lugar.
          </p>

          <form className="search-form" onSubmit={handleSubmit}>
            <label className="sr-only" htmlFor="product-search">
              Producto que deseas buscar
            </label>

            <input
              id="product-search"
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Ejemplo: laptop, celular o audífonos"
              minLength={2}
              maxLength={100}
              disabled={loading}
              required
            />

            <button type="submit" disabled={loading}>
              {loading ? 'Buscando…' : 'Buscar productos'}
            </button>
          </form>

          <div className="providers">
            <span>Disponible:</span>
            <strong>Mercado Libre</strong>
            <span className="separator">•</span>
            <span>Más tiendas próximamente</span>
          </div>
        </section>

        {error && (
          <section className="status-message error-message">
            <strong>No pudimos completar la búsqueda</strong>
            <p>{error}</p>
          </section>
        )}

        {loading && (
          <section className="status-message">
            <span className="loader" aria-hidden="true" />
            <strong>Consultando las tiendas disponibles…</strong>
          </section>
        )}

        {!loading && !error && !result && (
          <section className="results">
            <div className="empty-state">
              <span className="empty-icon">⌕</span>
              <h2>Tus resultados aparecerán aquí</h2>
              <p>
                Escribe el producto que necesitas para comenzar.
              </p>
            </div>
          </section>
        )}

        {!loading && result && (
          <section className="results results-content">
            <div className="results-header">
              <div>
                <span className="eyebrow">Resultados</span>
                <h2>Productos para “{result.query}”</h2>
              </div>

              <strong>
                {result.total}{' '}
                {result.total === 1 ? 'producto' : 'productos'}
              </strong>
            </div>

            {result.warning && (
              <div className="warning-message">
                {result.warning}
              </div>
            )}

            {result.products.length > 0 ? (
              <div className="product-grid">
                {result.products.map((product) => (
                  <ProductCard
                    key={`${product.tienda}-${product.id}`}
                    product={product}
                  />
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <span className="empty-icon">⌕</span>
                <h2>No encontramos productos</h2>
                <p>Prueba con otras palabras de búsqueda.</p>
              </div>
            )}
          </section>
        )}
      </main>

      <footer>
        <p>
          Dame Precio no realiza ventas. Las compras se completan
          directamente en el sitio oficial de cada tienda.
        </p>
      </footer>
    </div>
  )
}

export default App
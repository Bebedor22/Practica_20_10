import { type FormEvent, useState } from 'react'
import { useCourses } from '../hooks/useCourses'
import { CourseCard } from './CourseCard'

const CATEGORIES = [
  'Programación',
  'Diseño',
  'Marketing',
  'Negocios',
  'Artes',
  'Ciencias',
  'Otros',
]

export function CourseCatalog() {
  const { items, total, page, totalPages, loading, error, setPage, setFilters, refetch } =
    useCourses()
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')

  const handleSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFilters({ q: query.trim() || undefined, category: category || undefined })
  }

  const handleCategory = (nextCategory: string) => {
    setCategory(nextCategory)
    setFilters({ q: query.trim() || undefined, category: nextCategory || undefined })
  }

  return (
    <div className="page">
      <header className="site-header">
        <a className="site-header__brand" href="/">
          Roadmap de Cursos
        </a>
        <span className="site-header__hint">Catálogo comunitario</span>
      </header>

      <main className="catalog">
        <div className="catalog__heading">
          <div>
            <h1>Catálogo comunitario</h1>
            <p>
              Cursos gratuitos aportados y validados por la comunidad para armar
              tu roadmap.
            </p>
          </div>
          {!loading && !error && <span className="catalog__count">{total} cursos</span>}
        </div>

        <form className="filters" onSubmit={handleSearch} role="search">
          <label className="field field--grow">
            <span>Buscar</span>
            <input
              type="search"
              value={query}
              placeholder="Título, tema o docente"
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
          <label className="field">
            <span>Categoría</span>
            <select
              value={category}
              onChange={(event) => handleCategory(event.target.value)}
            >
              <option value="">Todas</option>
              {CATEGORIES.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" className="button">
            Buscar
          </button>
        </form>

        {loading && (
          <div className="skeleton-grid" aria-label="Cargando cursos" aria-busy="true">
            {Array.from({ length: 3 }, (_, index) => (
              <div className="skeleton-card" key={index} />
            ))}
          </div>
        )}

        {!loading && error && (
          <section className="state-panel" role="alert">
            <h2>No pudimos cargar el catálogo</h2>
            <p>{error}</p>
            <button type="button" className="button" onClick={refetch}>
              Reintentar
            </button>
          </section>
        )}

        {!loading && !error && items.length === 0 && (
          <section className="state-panel">
            <h2>Todavía no hay cursos publicados</h2>
            <p>
              Cuando la comunidad aporte y valide cursos, van a aparecer en este
              catálogo.
            </p>
          </section>
        )}

        {!loading && !error && items.length > 0 && (
          <>
            <div className="course-grid">
              {items.map((course) => (
                <CourseCard key={course.id} course={course} />
              ))}
            </div>
            <nav className="pagination" aria-label="Paginación del catálogo">
              <button
                type="button"
                className="button button--secondary"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
              >
                Anterior
              </button>
              <span>
                Página {page} de {Math.max(totalPages, 1)}
              </span>
              <button
                type="button"
                className="button button--secondary"
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
              >
                Siguiente
              </button>
            </nav>
          </>
        )}
      </main>
    </div>
  )
}

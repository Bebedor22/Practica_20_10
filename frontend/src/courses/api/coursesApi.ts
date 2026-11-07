import type { CoursesPage } from '../types'

export interface FetchCoursesParams {
  page: number
  limit: number
  q?: string
  category?: string
}

export async function fetchCourses(
  params: FetchCoursesParams,
  signal?: AbortSignal,
): Promise<CoursesPage> {
  const search = new URLSearchParams({
    page: String(params.page),
    limit: String(params.limit),
  })

  if (params.q) {
    search.set('q', params.q)
  }
  if (params.category) {
    search.set('category', params.category)
  }

  const response = await fetch(`/api/courses?${search.toString()}`, { signal })

  if (!response.ok) {
    throw new Error(`No se pudo cargar el catálogo (HTTP ${response.status})`)
  }

  return (await response.json()) as CoursesPage
}

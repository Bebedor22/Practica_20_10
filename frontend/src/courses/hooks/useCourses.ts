import { useCallback, useEffect, useState } from 'react'
import { fetchCourses } from '../api/coursesApi'
import type { Course } from '../types'

export interface CourseFilters {
  q?: string
  category?: string
}

export interface UseCoursesResult {
  items: Course[]
  total: number
  page: number
  totalPages: number
  loading: boolean
  error: string | null
  setPage: (page: number) => void
  setFilters: (filters: CourseFilters) => void
  refetch: () => void
}

export function useCourses(pageSize = 12): UseCoursesResult {
  const [page, setPageState] = useState(1)
  const [filters, setFiltersState] = useState<CourseFilters>({})
  const [refreshKey, setRefreshKey] = useState(0)
  const [items, setItems] = useState<Course[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    fetchCourses({ page, limit: pageSize, ...filters }, controller.signal)
      .then((data) => {
        setItems(data.items)
        setTotal(data.total)
        setTotalPages(data.totalPages)
      })
      .catch((cause: unknown) => {
        if (controller.signal.aborted) {
          return
        }
        setItems([])
        setTotal(0)
        setTotalPages(0)
        setError(
          cause instanceof Error ? cause.message : 'Error inesperado al cargar',
        )
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      })

    return () => controller.abort()
  }, [page, pageSize, filters, refreshKey])

  const setPage = useCallback((nextPage: number) => {
    setLoading(true)
    setError(null)
    setPageState(Math.max(1, nextPage))
  }, [])

  const setFilters = useCallback((nextFilters: CourseFilters) => {
    setLoading(true)
    setError(null)
    setFiltersState(nextFilters)
    setPageState(1)
  }, [])

  const refetch = useCallback(() => {
    setLoading(true)
    setError(null)
    setRefreshKey((current) => current + 1)
  }, [])

  return {
    items,
    total,
    page,
    totalPages,
    loading,
    error,
    setPage,
    setFilters,
    refetch,
  }
}

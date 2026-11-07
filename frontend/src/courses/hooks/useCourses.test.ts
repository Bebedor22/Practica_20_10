import { act, cleanup, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { Course, CoursesPage } from '../types'
import { useCourses } from './useCourses'

const fetchMock = vi.fn<typeof fetch>()

function makeCourse(overrides: Partial<Course> = {}): Course {
  return {
    id: 1,
    title: 'Curso de prueba',
    version: '2026.1',
    year: 2025,
    category: 'Programación',
    theme: 'Python',
    url: 'https://example.com/curso',
    instructor: 'Ada Lovelace',
    has_quiz: false,
    requires_exam: false,
    extends_certificate: false,
    organization: null,
    validated: true,
    user_id: 1,
    ...overrides,
  }
}

function makePage(overrides: Partial<CoursesPage> = {}): CoursesPage {
  return {
    items: [makeCourse()],
    total: 1,
    page: 1,
    limit: 12,
    totalPages: 1,
    hasNext: false,
    hasPrev: false,
    ...overrides,
  }
}

function jsonResponse(body: CoursesPage): Response {
  return {
    ok: true,
    status: 200,
    json: async () => body,
  } as Response
}

function requestUrl(callIndex: number): URL {
  const input = fetchMock.mock.calls[callIndex]?.[0]
  return new URL(String(input), 'http://localhost')
}

beforeEach(() => {
  fetchMock.mockReset()
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('useCourses', () => {
  it('loads the first page with the default page size', async () => {
    const page = makePage({
      items: [makeCourse({ id: 7 })],
      total: 3,
    })
    fetchMock.mockResolvedValue(jsonResponse(page))

    const { result } = renderHook(() => useCourses())

    expect(result.current.loading).toBe(true)
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.items).toHaveLength(1)
    expect(result.current.items[0]?.id).toBe(7)
    expect(result.current.total).toBe(3)
    expect(result.current.totalPages).toBe(1)
    expect(result.current.error).toBeNull()
    expect(requestUrl(0).searchParams.get('page')).toBe('1')
    expect(requestUrl(0).searchParams.get('limit')).toBe('12')
  })

  it('uses the provided page size and fetches the next page', async () => {
    fetchMock
      .mockResolvedValueOnce(
        jsonResponse(
          makePage({
            page: 1,
            limit: 5,
            total: 7,
            totalPages: 2,
            hasNext: true,
          }),
        ),
      )
      .mockResolvedValueOnce(
        jsonResponse(
          makePage({
            page: 2,
            limit: 5,
            total: 7,
            totalPages: 2,
            hasPrev: true,
          }),
        ),
      )

    const { result } = renderHook(() => useCourses(5))
    await waitFor(() => expect(result.current.loading).toBe(false))

    act(() => result.current.setPage(2))
    await waitFor(() => expect(result.current.page).toBe(2))
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(requestUrl(1).searchParams.get('page')).toBe('2')
    expect(requestUrl(1).searchParams.get('limit')).toBe('5')
  })

  it('clamps the page to one without refetching the same page', async () => {
    fetchMock.mockResolvedValue(jsonResponse(makePage()))
    const { result } = renderHook(() => useCourses())
    await waitFor(() => expect(result.current.loading).toBe(false))

    act(() => result.current.setPage(0))

    expect(result.current.page).toBe(1)
    expect(result.current.loading).toBe(false)
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('resets to page one and sends filters when filters change', async () => {
    fetchMock.mockResolvedValue(jsonResponse(makePage()))
    const { result } = renderHook(() => useCourses())
    await waitFor(() => expect(result.current.loading).toBe(false))

    act(() => result.current.setPage(2))
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    await waitFor(() => expect(result.current.loading).toBe(false))

    act(() =>
      result.current.setFilters({ q: 'python', category: 'Programación' }),
    )
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3))
    await waitFor(() => expect(result.current.loading).toBe(false))

    const lastRequest = requestUrl(2)
    expect(result.current.page).toBe(1)
    expect(lastRequest.searchParams.get('page')).toBe('1')
    expect(lastRequest.searchParams.get('q')).toBe('python')
    expect(lastRequest.searchParams.get('category')).toBe('Programación')
  })

  it('refetches the current page when refetch is called', async () => {
    fetchMock.mockResolvedValue(jsonResponse(makePage()))
    const { result } = renderHook(() => useCourses())
    await waitFor(() => expect(result.current.loading).toBe(false))

    act(() => result.current.refetch())
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(requestUrl(1).searchParams.get('page')).toBe('1')
  })

  it('clears data and exposes the message when the request fails', async () => {
    fetchMock.mockRejectedValue(new Error('falló la red'))
    const { result } = renderHook(() => useCourses())

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.error).toBe('falló la red')
    expect(result.current.items).toEqual([])
    expect(result.current.total).toBe(0)
    expect(result.current.totalPages).toBe(0)
  })

  it('uses a generic message for non-Error failures', async () => {
    fetchMock.mockRejectedValue('boom')
    const { result } = renderHook(() => useCourses())

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.error).toBe('Error inesperado al cargar')
  })

  it('aborts the in-flight request on unmount', () => {
    let signal: AbortSignal | null | undefined
    fetchMock.mockImplementation((_input, init) => {
      signal = init?.signal
      return new Promise<Response>(() => {})
    })

    const { unmount } = renderHook(() => useCourses())
    expect(signal).toBeDefined()

    unmount()

    expect(signal?.aborted).toBe(true)
  })
})

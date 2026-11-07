export interface Course {
  id: number
  title: string
  version: string
  year: number
  category: string
  theme: string
  url: string
  instructor: string
  has_quiz: boolean
  requires_exam: boolean
  extends_certificate: boolean
  organization: string | null
  validated: boolean
  user_id: number
}

export interface CoursesPage {
  items: Course[]
  total: number
  page: number
  limit: number
  totalPages: number
  hasNext: boolean
  hasPrev: boolean
}

import type { Course } from '../types'

interface CourseCardProps {
  course: Course
}

const ATTRIBUTES: Array<{ key: keyof Course; label: string }> = [
  { key: 'has_quiz', label: 'Cuestionarios' },
  { key: 'requires_exam', label: 'Examen' },
  { key: 'extends_certificate', label: 'Certificado' },
]

export function CourseCard({ course }: CourseCardProps) {
  return (
    <article className="course-card">
      <div className="course-card__meta">
        <span className="chip">{course.category}</span>
        <span className="course-card__year">{course.year}</span>
      </div>
      <h2>{course.title}</h2>
      <p className="course-card__theme">{course.theme}</p>
      <p className="course-card__instructor">{course.instructor}</p>
      <ul className="course-card__attributes" aria-label="Atributos del curso">
        {ATTRIBUTES.map(({ key, label }) => (
          <li key={key} className={course[key] ? 'is-on' : 'is-off'}>
            {label}
          </li>
        ))}
      </ul>
      <a
        className="course-card__link"
        href={course.url}
        target="_blank"
        rel="noreferrer"
      >
        Ver curso
      </a>
    </article>
  )
}

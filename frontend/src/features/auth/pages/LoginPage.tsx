import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useForm } from '@tanstack/react-form'
import { useMutation } from '@tanstack/react-query'
import { useAuth } from '../../../store/authStore'
import { EstadoError } from '../../../shared/components/States'

export function LoginPage() {
  const login = useAuth((state) => state.login)
  const navigate = useNavigate()
  const location = useLocation()
  const mutation = useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      login(username, password),
    onSuccess: (user) => {
      const state: unknown = location.state
      const from =
        state && typeof state === 'object' && 'from' in state && typeof state.from === 'string'
          ? state.from
          : null
      navigate(from ?? (user.role === 'admin' ? '/admin/resumen' : '/'), { replace: true })
    },
  })
  const form = useForm({
    defaultValues: { username: '', password: '' },
    onSubmit: async ({ value }) => {
      try {
        await mutation.mutateAsync(value)
      } catch {
        /* rendered below */
      }
    },
  })
  return (
    <div className="auth-layout">
      <div className="auth-story">
        <span className="eyebrow">VOLVÉ A LO RICO</span>
        <h1>
          Tu próxima
          <br />
          comida favorita
          <br />
          <em>te está esperando.</em>
        </h1>
        <img src="/images/hero-burger.svg" alt="Hamburguesa de la casa" />
      </div>
      <section className="form-card">
        <span className="eyebrow">¡QUÉ BUENO VERTE!</span>
        <h2>Ingresar</h2>
        <p>Entrá a tu cuenta para hacer y seguir tus pedidos.</p>
        <form
          onSubmit={(event) => {
            event.preventDefault()
            void form.handleSubmit()
          }}
        >
          <form.Field
            name="username"
            validators={{
              onChange: ({ value }) => (!value.trim() ? 'Ingresá tu usuario' : undefined),
            }}
          >
            {(field) => (
              <label>
                Usuario
                <input
                  name="username"
                  autoComplete="username"
                  required
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(event) => field.handleChange(event.target.value)}
                />
              </label>
            )}
          </form.Field>
          <form.Field name="password">
            {(field) => (
              <label>
                Contraseña
                <input
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={field.state.value}
                  onChange={(event) => field.handleChange(event.target.value)}
                />
              </label>
            )}
          </form.Field>
          <button disabled={mutation.isPending}>
            {mutation.isPending ? 'Ingresando…' : 'Ingresar'}
          </button>
        </form>
        {mutation.isError && <EstadoError error={mutation.error} />}
        <p className="form-foot">
          ¿Primera vez por acá? <Link to="/register">Creá tu cuenta</Link>
        </p>
      </section>
    </div>
  )
}

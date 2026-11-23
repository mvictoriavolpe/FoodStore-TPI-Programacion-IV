import { Link, useNavigate } from 'react-router-dom'
import { useForm } from '@tanstack/react-form'
import { useMutation } from '@tanstack/react-query'
import { authApi } from '../api/auth'
import { EstadoError } from '../../../shared/components/States'

const labels = {
  username: 'Usuario',
  full_name: 'Nombre completo',
  email: 'Email',
  password: 'Contraseña',
}
export function RegisterPage() {
  const navigate = useNavigate()
  const mutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: () => navigate('/login', { state: { registered: true } }),
  })
  const form = useForm({
    defaultValues: { username: '', full_name: '', email: '', password: '' },
    onSubmit: async ({ value }) => {
      try {
        await mutation.mutateAsync(value)
      } catch {
        /* rendered below */
      }
    },
  })
  return (
    <section className="form-card centered-form">
      <span className="eyebrow">BIENVENIDO A LA MESA</span>
      <h1>Creá tu cuenta</h1>
      <p>Unos pocos datos y ya podés pedir algo rico.</p>
      <form
        onSubmit={(event) => {
          event.preventDefault()
          void form.handleSubmit()
        }}
      >
        {(['full_name', 'username', 'email', 'password'] as const).map((key) => (
          <form.Field
            key={key}
            name={key}
            validators={{
              onChange: ({ value }) =>
                !value.trim()
                  ? 'Completá este campo'
                  : key === 'password' &&
                      (value.length < 8 || new TextEncoder().encode(value).length > 72)
                    ? 'Usá al menos 8 caracteres y hasta 72 bytes'
                    : undefined,
            }}
          >
            {(field) => (
              <label>
                {labels[key]}
                <input
                  name={key}
                  type={key === 'password' ? 'password' : key === 'email' ? 'email' : 'text'}
                  autoComplete={
                    key === 'password' ? 'new-password' : key === 'full_name' ? 'name' : key
                  }
                  required
                  minLength={key === 'password' ? 8 : key === 'username' ? 3 : 1}
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(event) => field.handleChange(event.target.value)}
                />
                {field.state.meta.isTouched && field.state.meta.errors.length > 0 && (
                  <small className="field-error">{field.state.meta.errors.join(', ')}</small>
                )}
              </label>
            )}
          </form.Field>
        ))}
        <button disabled={mutation.isPending}>
          {mutation.isPending ? 'Creando cuenta…' : 'Crear cuenta'}
        </button>
      </form>
      {mutation.isError && <EstadoError error={mutation.error} />}
      <p className="form-foot">
        ¿Ya tenés cuenta? <Link to="/login">Ingresá</Link>
      </p>
    </section>
  )
}

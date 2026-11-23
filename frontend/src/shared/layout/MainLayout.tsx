import { useState } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { useAuth } from '../../store/authStore'
import { useCart } from '../../store/cartStore'
import { handleApiError } from '../api/handleApiError'

export function MainLayout() {
  const user = useAuth((state) => state.user)
  const logout = useAuth((state) => state.logout)
  const count = useCart((state) => state.items.reduce((sum, item) => sum + item.cantidad, 0))
  const navigate = useNavigate()
  const [menu, setMenu] = useState(false)
  const mutation = useMutation({
    mutationFn: logout,
    onSuccess: () => {
      setMenu(false)
      navigate('/login')
    },
  })
  return (
    <>
      <header className="site-header">
        <div className="header-inner">
          <Link className="brand" to="/" aria-label="Food Store, inicio">
            <span className="brand-mark" aria-hidden="true">
              f.
            </span>
            <span>
              food<span className="brand-light">store</span>
              <small>HECHO CON GANAS</small>
            </span>
          </Link>
          <button
            className="mobile-menu secondary"
            aria-expanded={menu}
            aria-controls="main-nav"
            onClick={() => setMenu(!menu)}
          >
            Menú
          </button>
          <nav id="main-nav" className={menu ? 'open' : ''} aria-label="Navegación principal">
            <NavLink to="/" end onClick={() => setMenu(false)}>
              Menú
            </NavLink>
            {user && (
              <NavLink to="/mis-pedidos" onClick={() => setMenu(false)}>
                Mis pedidos
              </NavLink>
            )}
            {user?.role === 'admin' && (
              <NavLink to="/admin/resumen" onClick={() => setMenu(false)}>
                Administración
              </NavLink>
            )}
            <NavLink className="cart-link" to="/carrito" onClick={() => setMenu(false)}>
              Carrito <span>{count}</span>
            </NavLink>
            {user ? (
              <div className="session-nav">
                <span>
                  {user.full_name}
                  <small>{user.role === 'admin' ? 'Administrador' : 'Cliente'}</small>
                </span>
                <button
                  className="text-button"
                  disabled={mutation.isPending}
                  onClick={() => mutation.mutate()}
                >
                  Cerrar sesión
                </button>
              </div>
            ) : (
              <Link className="button small" to="/login" onClick={() => setMenu(false)}>
                Ingresar
              </Link>
            )}
          </nav>
        </div>
      </header>
      {mutation.isError && (
        <div className="container error-box" role="alert">
          {handleApiError(mutation.error)}
        </div>
      )}
      <main className="container">
        <Outlet />
      </main>
      <footer className="site-footer">
        <div>
          <Link className="footer-brand" to="/">
            foodstore<span>®</span>
          </Link>
          <p>Buena comida. Buenos momentos.</p>
        </div>
        <p>
          Food Store · UTN Programación 4<br />
          <span>Preparado con dedicación, pedido por vos.</span>
        </p>
      </footer>
    </>
  )
}

export function AdminLayout() {
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">EL NEGOCIO, A MANO</span>
          <h1>Administración</h1>
        </div>
        <span className="admin-tag">Panel del negocio</span>
      </div>
      <nav className="admin-tabs" aria-label="Administración">
        {[
          ['resumen', 'Resumen'],
          ['categorias', 'Categorías'],
          ['productos', 'Productos'],
          ['pedidos', 'Pedidos'],
          ['usuarios', 'Usuarios'],
        ].map(([path, label]) => (
          <NavLink key={path} to={`/admin/${path}`}>
            {label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </>
  )
}

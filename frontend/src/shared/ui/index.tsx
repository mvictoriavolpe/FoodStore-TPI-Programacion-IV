import { useEffect, useRef, type ReactNode } from 'react'
import type { OrderState } from '../../features/pedidos/types'
import { stateLabels } from '../../features/pedidos/types'

export const money = (amount: number) =>
  new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    maximumFractionDigits: 2,
  }).format(amount)
export const dateTime = (value: string) =>
  new Date(/Z$|[+-]\d{2}:\d{2}$/.test(value) ? value : `${value}Z`).toLocaleString('es-AR')

export function BadgeEstado({ state }: { state: OrderState }) {
  return <span className={`badge ${state.toLowerCase()}`}>{stateLabels[state]}</span>
}

export function Modal({
  title,
  close,
  children,
}: {
  title: string
  close: () => void
  children: ReactNode
}) {
  const ref = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    ref.current?.showModal()
  }, [])
  return (
    <dialog
      ref={ref}
      onCancel={(event) => {
        event.preventDefault()
        close()
      }}
      onClick={(event) => {
        if (event.target === event.currentTarget) close()
      }}
    >
      <div className="modal-heading">
        <h2>{title}</h2>
        <button className="secondary" aria-label="Cerrar" onClick={close}>
          Cerrar
        </button>
      </div>
      {children}
    </dialog>
  )
}

export function FoodImage({
  src,
  name,
  className = '',
}: {
  src: string
  name: string
  className?: string
}) {
  return (
    <img
      className={`food-image ${className}`}
      src={src || '/images/burger.svg'}
      alt={name}
      loading="lazy"
      onError={(event) => {
        event.currentTarget.onerror = null
        event.currentTarget.src = '/images/burger.svg'
      }}
    />
  )
}

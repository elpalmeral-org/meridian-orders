/** Tipos de la API de Meridian Orders (espejo de apps/backend/src/meridian_orders/schemas.py). */

export type OrderStatus = 'pending' | 'confirmed' | 'shipped' | 'cancelled';

export const ORDER_STATUSES: readonly OrderStatus[] = [
  'pending',
  'confirmed',
  'shipped',
  'cancelled',
];

export const STATUS_LABELS: Record<OrderStatus, string> = {
  pending: 'Pendiente',
  confirmed: 'Confirmado',
  shipped: 'Enviado',
  cancelled: 'Cancelado',
};

/** Texto del botón que lleva a cada estado (verbos, no estados). */
export const ACTION_LABELS: Record<OrderStatus, string> = {
  pending: 'Reabrir',
  confirmed: 'Confirmar',
  shipped: 'Enviar',
  cancelled: 'Cancelar',
};

/** Misma máquina de estados que el backend: solo se ofrecen las transiciones permitidas. */
export const ALLOWED_TRANSITIONS: Record<OrderStatus, readonly OrderStatus[]> = {
  pending: ['confirmed', 'cancelled'],
  confirmed: ['shipped', 'cancelled'],
  shipped: [],
  cancelled: [],
};

export interface Order {
  id: string;
  customer_name: string;
  customer_email: string;
  total_amount: string; // decimal serializado como texto: sin errores de coma flotante
  currency: string;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
}

export interface OrderList {
  items: Order[];
  total: number;
}

export interface OrderCreate {
  customer_name: string;
  customer_email: string;
  total_amount: string;
  currency?: string;
}

export interface ApiInfo {
  version: string;
  environment: string;
}

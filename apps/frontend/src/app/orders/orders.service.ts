import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiInfo, Order, OrderCreate, OrderList, OrderStatus } from './order.model';

/** Cliente de la API. Rutas relativas: front y API comparten host (`/` y `/api`). */
@Injectable({ providedIn: 'root' })
export class OrdersService {
  private readonly http = inject(HttpClient);
  private readonly base = '/api/orders';

  list(status: OrderStatus | null): Observable<OrderList> {
    let params = new HttpParams().set('limit', 100);
    if (status) {
      params = params.set('status', status);
    }
    return this.http.get<OrderList>(this.base, { params });
  }

  create(order: OrderCreate): Observable<Order> {
    return this.http.post<Order>(this.base, order);
  }

  changeStatus(id: string, status: OrderStatus): Observable<Order> {
    return this.http.patch<Order>(`${this.base}/${id}/status`, { status });
  }

  info(): Observable<ApiInfo> {
    return this.http.get<ApiInfo>('/api/info');
  }
}

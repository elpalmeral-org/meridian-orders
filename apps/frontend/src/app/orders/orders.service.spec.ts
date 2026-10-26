import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { OrdersService } from './orders.service';

describe('OrdersService', () => {
  let service: OrdersService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(OrdersService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('lista sin filtro', () => {
    service.list(null).subscribe();
    const req = http.expectOne((r) => r.url === '/api/orders');
    expect(req.request.params.has('status')).toBe(false);
    expect(req.request.params.get('limit')).toBe('100');
    req.flush({ items: [], total: 0 });
  });

  it('lista filtrando por estado', () => {
    service.list('confirmed').subscribe();
    const req = http.expectOne((r) => r.url === '/api/orders');
    expect(req.request.params.get('status')).toBe('confirmed');
    req.flush({ items: [], total: 0 });
  });

  it('crea pedidos con POST', () => {
    const body = { customer_name: 'Acme', customer_email: 'a@acme.example', total_amount: '9.90' };
    service.create(body).subscribe();
    const req = http.expectOne('/api/orders');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(body);
    req.flush({});
  });

  it('cambia el estado con PATCH', () => {
    service.changeStatus('abc', 'shipped').subscribe();
    const req = http.expectOne('/api/orders/abc/status');
    expect(req.request.method).toBe('PATCH');
    expect(req.request.body).toEqual({ status: 'shipped' });
    req.flush({});
  });
});

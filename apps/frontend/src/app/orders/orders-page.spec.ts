import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { registerLocaleData } from '@angular/common';
import localeEs from '@angular/common/locales/es';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Order } from './order.model';
import { OrdersPage } from './orders-page';

registerLocaleData(localeEs);

function order(overrides: Partial<Order> = {}): Order {
  return {
    id: 'o-1',
    customer_name: 'Acme Logística',
    customer_email: 'compras@acme.example',
    total_amount: '149.90',
    currency: 'EUR',
    status: 'pending',
    created_at: '2026-10-26T10:00:00Z',
    updated_at: '2026-10-26T10:00:00Z',
    ...overrides,
  };
}

describe('OrdersPage', () => {
  let fixture: ComponentFixture<OrdersPage>;
  let http: HttpTestingController;
  const el = (): HTMLElement => fixture.nativeElement as HTMLElement;

  async function render(items: Order[]): Promise<void> {
    fixture = TestBed.createComponent(OrdersPage);
    fixture.detectChanges();
    http.expectOne((r) => r.url === '/api/orders').flush({ items, total: items.length });
    await fixture.whenStable();
    fixture.detectChanges();
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrdersPage],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('muestra un mensaje cuando no hay pedidos', async () => {
    await render([]);
    expect(el().querySelector('.empty')?.textContent).toContain('No hay pedidos');
  });

  it('pinta los pedidos con su importe y estado', async () => {
    await render([order()]);
    const row = el().querySelector('tbody tr');
    expect(row?.textContent).toContain('Acme Logística');
    expect(row?.textContent).toContain('149,90');
    expect(row?.textContent).toContain('Pendiente');
  });

  it('solo ofrece las transiciones permitidas', async () => {
    await render([order({ id: 'p' }), order({ id: 's', status: 'shipped' })]);
    const [pending, shipped] = Array.from(el().querySelectorAll('tbody tr'));
    expect(pending.querySelector('[data-testid="to-confirmed"]')).not.toBeNull();
    expect(pending.querySelector('[data-testid="to-cancelled"]')).not.toBeNull();
    expect(pending.querySelector('[data-testid="to-shipped"]')).toBeNull();
    expect(shipped.querySelectorAll('.actions button').length).toBe(0);
  });

  it('cambia el estado y recarga la lista', async () => {
    await render([order()]);
    (el().querySelector('[data-testid="to-confirmed"]') as HTMLButtonElement).click();
    const patch = http.expectOne('/api/orders/o-1/status');
    expect(patch.request.body).toEqual({ status: 'confirmed' });
    patch.flush(order({ status: 'confirmed' }));
    http.expectOne((r) => r.url === '/api/orders').flush({ items: [], total: 0 });
  });

  it('filtra por estado', async () => {
    await render([]);
    const select = el().querySelector('[data-testid="status-filter"]') as HTMLSelectElement;
    select.value = 'shipped';
    select.dispatchEvent(new Event('change'));
    const req = http.expectOne((r) => r.url === '/api/orders');
    expect(req.request.params.get('status')).toBe('shipped');
    req.flush({ items: [], total: 0 });
  });

  it('no envía el formulario si no es válido y sí cuando lo es', async () => {
    await render([]);
    const form = el().querySelector('form') as HTMLFormElement;
    form.dispatchEvent(new Event('submit'));
    http.expectNone('/api/orders');

    const set = (name: string, value: string): void => {
      const input = el().querySelector(`[formControlName="${name}"]`) as HTMLInputElement;
      input.value = value;
      input.dispatchEvent(new Event('input'));
    };
    set('customer_name', 'Beta SL');
    set('customer_email', 'ops@beta.example');
    set('total_amount', '20.00');
    form.dispatchEvent(new Event('submit'));

    const post = http.expectOne((r) => r.method === 'POST' && r.url === '/api/orders');
    expect(post.request.body).toEqual({
      customer_name: 'Beta SL',
      customer_email: 'ops@beta.example',
      total_amount: '20.00',
    });
    post.flush(order());
    http
      .expectOne((r) => r.method === 'GET' && r.url === '/api/orders')
      .flush({ items: [], total: 0 });
  });

  it('muestra el detalle de error que devuelve la API', async () => {
    await render([order()]);
    (el().querySelector('[data-testid="to-confirmed"]') as HTMLButtonElement).click();
    http
      .expectOne('/api/orders/o-1/status')
      .flush(
        { detail: "No se puede pasar de 'pending' a 'confirmed'" },
        { status: 409, statusText: 'Conflict' },
      );
    await fixture.whenStable();
    fixture.detectChanges();
    expect(el().querySelector('[role="alert"]')?.textContent).toContain('No se puede pasar');
  });
});

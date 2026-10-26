import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { App } from './app';

describe('App', () => {
  let http: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('muestra el nombre del producto', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    http.expectOne('/api/info').flush({ version: '0.1.0', environment: 'dev' });
    http.expectOne((r) => r.url === '/api/orders').flush({ items: [], total: 0 });
    await fixture.whenStable();
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelector('h1')?.textContent).toContain('Meridian Orders');
  });

  it('muestra la versión y el entorno que informa la API', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    http.expectOne('/api/info').flush({ version: '1.2.3', environment: 'staging' });
    http.expectOne((r) => r.url === '/api/orders').flush({ items: [], total: 0 });
    await fixture.whenStable();
    const meta = (fixture.nativeElement as HTMLElement).querySelector(
      '[data-testid="api-version"]',
    );
    expect(meta?.textContent).toContain('v1.2.3');
    expect(meta?.textContent).toContain('staging');
  });
});

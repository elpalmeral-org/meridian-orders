import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';

import { OrdersPage } from './orders/orders-page';
import { OrdersService } from './orders/orders.service';

@Component({
  selector: 'app-root',
  imports: [OrdersPage],
  templateUrl: './app.html',
  styleUrl: './app.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App implements OnInit {
  private readonly api = inject(OrdersService);
  protected readonly version = signal<string | null>(null);
  protected readonly environment = signal<string | null>(null);

  ngOnInit(): void {
    this.api.info().subscribe({
      next: (info) => {
        this.version.set(info.version);
        this.environment.set(info.environment);
      },
      error: () => this.version.set(null),
    });
  }
}

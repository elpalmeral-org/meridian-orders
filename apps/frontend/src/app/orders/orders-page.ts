import { CurrencyPipe, DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import {
  ACTION_LABELS,
  ALLOWED_TRANSITIONS,
  ORDER_STATUSES,
  Order,
  OrderStatus,
  STATUS_LABELS,
} from './order.model';
import { OrdersService } from './orders.service';

@Component({
  selector: 'app-orders-page',
  imports: [ReactiveFormsModule, CurrencyPipe, DatePipe],
  templateUrl: './orders-page.html',
  styleUrl: './orders-page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrdersPage implements OnInit {
  private readonly api = inject(OrdersService);
  private readonly fb = inject(NonNullableFormBuilder);

  protected readonly statuses = ORDER_STATUSES;
  protected readonly labels = STATUS_LABELS;
  protected readonly actions = ACTION_LABELS;

  protected readonly orders = signal<Order[]>([]);
  protected readonly total = signal(0);
  protected readonly filter = signal<OrderStatus | null>(null);
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);

  protected readonly form = this.fb.group({
    customer_name: ['', [Validators.required, Validators.maxLength(200)]],
    customer_email: ['', [Validators.required, Validators.email]],
    total_amount: ['', [Validators.required, Validators.pattern(/^\d{1,10}(\.\d{1,2})?$/)]],
  });

  ngOnInit(): void {
    this.load();
  }

  protected transitionsFor(order: Order): readonly OrderStatus[] {
    return ALLOWED_TRANSITIONS[order.status];
  }

  protected setFilter(value: string): void {
    this.filter.set(value ? (value as OrderStatus) : null);
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.api.list(this.filter()).subscribe({
      next: (page) => {
        this.orders.set(page.items);
        this.total.set(page.total);
        this.error.set(null);
        this.loading.set(false);
      },
      error: (err: HttpErrorResponse) => this.fail(err),
    });
  }

  protected create(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.api.create(this.form.getRawValue()).subscribe({
      next: () => {
        this.form.reset();
        this.load();
      },
      error: (err: HttpErrorResponse) => this.fail(err),
    });
  }

  protected move(order: Order, target: OrderStatus): void {
    this.api.changeStatus(order.id, target).subscribe({
      next: () => this.load(),
      error: (err: HttpErrorResponse) => this.fail(err),
    });
  }

  private fail(err: HttpErrorResponse): void {
    const detail: unknown = (err.error as { detail?: unknown } | null)?.detail;
    this.error.set(
      typeof detail === 'string' ? detail : `Error ${err.status} al hablar con la API`,
    );
    this.loading.set(false);
  }
}

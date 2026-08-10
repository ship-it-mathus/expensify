import {
  Component,
  Input,
  OnChanges,
  SimpleChanges,
  ElementRef,
  ViewChild,
  AfterViewInit,
  OnDestroy
} from '@angular/core';
import {
  Chart,
  DoughnutController,
  BarController,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions
} from 'chart.js';

Chart.register(
  DoughnutController,
  BarController,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

// ─────────────────────────────────────────────
// Shared palette (vibrant, dark-mode friendly)
// ─────────────────────────────────────────────
const PALETTE = [
  '#6366f1', '#f59e0b', '#10b981', '#ef4444',
  '#3b82f6', '#ec4899', '#8b5cf6', '#14b8a6',
  '#f97316', '#06b6d4', '#a3e635', '#fb923c'
];

// ─────────────────────────────────────────────
// Donut Chart — Category Spending Breakdown
// ─────────────────────────────────────────────
@Component({
  selector: 'app-donut-chart',
  standalone: true,
  template: `
    <div style="position: relative; width: 100%; max-width: 280px; margin: 0 auto; overflow: hidden;">
      <canvas #canvas style="max-width: 100%;"></canvas>
      @if (!hasData) {
        <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 0.88rem;">
          No expense data this month
        </div>
      }
    </div>
  `
})
export class DonutChartComponent implements AfterViewInit, OnChanges, OnDestroy {
  @ViewChild('canvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  @Input() labels: string[] = [];
  @Input() values: number[] = [];

  private chart: Chart<'doughnut'> | null = null;
  hasData = false;

  ngAfterViewInit() { this.buildChart(); }

  ngOnChanges(changes: SimpleChanges) {
    this.hasData = this.values.some(v => v > 0);
    if (!this.chart) return;

    // Destroy and rebuild when going from no-data → has-data so Chart.js
    // renders cleanly instead of staying blank from the empty initialisation.
    const wasEmpty = (this.chart.data.datasets[0]?.data as number[] ?? []).every(v => !v);
    if (wasEmpty && this.hasData) {
      this.chart.destroy();
      this.chart = null;
      this.buildChart();
    } else {
      this.updateChart();
    }
  }

  ngOnDestroy() { this.chart?.destroy(); }

  private buildChart() {
    const ctx = this.canvasRef.nativeElement.getContext('2d')!;
    this.hasData = this.values.some(v => v > 0);

    this.chart = new Chart(ctx, {
      type: 'doughnut',
      data: this.getData(),
      options: this.getOptions()
    });
  }

  private updateChart() {
    if (!this.chart) return;
    this.hasData = this.values.some(v => v > 0);
    this.chart.data = this.getData();
    this.chart.update('active');
  }


  private getData(): ChartData<'doughnut'> {
    return {
      labels: this.labels,
      datasets: [{
        data: this.values,
        backgroundColor: PALETTE.slice(0, this.labels.length),
        borderColor: '#0f172a',
        borderWidth: 3,
        hoverOffset: 10
      }]
    };
  }

  private getOptions(): ChartOptions<'doughnut'> {
    return {
      responsive: true,
      maintainAspectRatio: true,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#94a3b8',
            font: { size: 12, family: 'Inter, sans-serif' },
            padding: 16,
            usePointStyle: true,
            pointStyleWidth: 8
          }
        },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#f1f5f9',
          bodyColor: '#94a3b8',
          borderColor: '#334155',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => {
              const val = ctx.parsed;
              const total = (ctx.dataset.data as number[]).reduce((a, b) => a + b, 0);
              const pct = total > 0 ? ((val / total) * 100).toFixed(1) : '0';
              return ` ₹${val.toLocaleString('en-IN')}  (${pct}%)`;
            }
          }
        }
      }
    };
  }
}

// ─────────────────────────────────────────────
// Bar Chart — Income vs Expense
// ─────────────────────────────────────────────
@Component({
  selector: 'app-bar-chart',
  standalone: true,
  template: `
    <div style="position: relative; width: 100%; overflow: hidden;">
      <canvas #canvas style="max-width: 100%; height: 220px;"></canvas>
    </div>
  `
})
export class BarChartComponent implements AfterViewInit, OnChanges, OnDestroy {
  @ViewChild('canvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  @Input() income = 0;
  @Input() expense = 0;
  @Input() savings = 0;
  @Input() monthLabel = '';

  private chart: Chart<'bar'> | null = null;

  ngAfterViewInit() { this.buildChart(); }
  ngOnChanges() { if (this.chart) this.updateChart(); }
  ngOnDestroy() { this.chart?.destroy(); }

  private buildChart() {
    const ctx = this.canvasRef.nativeElement.getContext('2d')!;
    this.chart = new Chart(ctx, {
      type: 'bar',
      data: this.getData(),
      options: this.getOptions()
    });
  }

  private updateChart() {
    if (!this.chart) return;
    this.chart.data = this.getData();
    this.chart.update('active');
  }

  private getData(): ChartData<'bar'> {
    return {
      labels: ['Income', 'Expense', 'Net Savings'],
      datasets: [{
        label: this.monthLabel || 'This Month',
        data: [this.income, this.expense, this.savings],
        backgroundColor: ['rgba(16,185,129,0.85)', 'rgba(239,68,68,0.85)', 'rgba(99,102,241,0.85)'],
        borderColor: ['#10b981', '#ef4444', '#6366f1'],
        borderWidth: 2,
        borderRadius: 10,
        borderSkipped: false
      }]
    };
  }

  private getOptions(): ChartOptions<'bar'> {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#f1f5f9',
          bodyColor: '#94a3b8',
          borderColor: '#334155',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => ` ₹${(ctx.parsed.y as number).toLocaleString('en-IN')}`
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#94a3b8', font: { size: 12, family: 'Inter, sans-serif' } }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.06)' },
          ticks: {
            color: '#94a3b8',
            font: { size: 11, family: 'Inter, sans-serif' },
            callback: (val) => `₹${Number(val).toLocaleString('en-IN')}`
          }
        }
      }
    };
  }
}

// ─────────────────────────────────────────────
// Insights Carousel — Rotating Stat Cards
// ─────────────────────────────────────────────
import { CommonModule, CurrencyPipe } from '@angular/common';
import { InsightCard } from '../models/expensify.models';

@Component({
  selector: 'app-insights-carousel',
  standalone: true,
  imports: [CommonModule, CurrencyPipe],
  template: `
    <div style="position: relative; overflow: hidden;">
      @if (cards.length > 0) {
        <!-- Current card -->
        <div
          [style.opacity]="visible ? '1' : '0'"
          style="transition: opacity 0.5s ease; display: flex; align-items: center; gap: 16px; background: #0f172a; border-radius: 16px; padding: 20px 24px; border: 1px solid #1e293b; cursor: pointer; min-height: 88px;"
          (click)="advance()">

          <!-- Icon bubble -->
          <div [style.background]="card.color + '1a'" [style.border]="'1.5px solid ' + card.color + '55'"
               style="width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
            <span class="material-symbols-outlined" [style.color]="card.color" style="font-size: 1.5rem;">{{ card.icon }}</span>
          </div>

          <!-- Text -->
          <div style="flex: 1; min-width: 0;">
            <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 4px;">{{ card.label }}</div>
            <div style="font-size: 1.6rem; font-weight: 800; line-height: 1;" [style.color]="card.color">
              @if (card.value === null || card.value === undefined) {
                <span style="font-size: 1rem; color: var(--text-muted); font-weight: 500;">No data yet</span>
              } @else if (card.format === 'currency') {
                {{ card.value | currency:'INR':'symbol':'1.0-0' }}
              } @else {
                {{ card.value.toFixed(1) }}%
              }
            </div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 3px;">{{ card.sublabel }}</div>
          </div>

          <!-- Progress dots -->
          <div style="display: flex; flex-direction: column; gap: 5px; align-items: center; flex-shrink: 0;">
            @for (c of cards; track c.id; let i = $index) {
              <div [style.background]="i === currentIndex ? card.color : '#334155'"
                   [style.height]="i === currentIndex ? '20px' : '6px'"
                   style="width: 4px; border-radius: 4px; transition: all 0.3s ease;"></div>
            }
          </div>
        </div>

        <!-- Progress bar -->
        <div style="height: 2px; background: #1e293b; border-radius: 1px; margin-top: 8px; overflow: hidden;">
          <div [style.width]="progressPct + '%'" [style.background]="card.color"
               style="height: 100%; border-radius: 1px; transition: width 0.1s linear;"></div>
        </div>
      } @else {
        <div style="color: var(--text-muted); font-size: 0.88rem; text-align: center; padding: 24px;">
          No insight data yet — add some transactions!
        </div>
      }
    </div>
  `
})
export class InsightsCarouselComponent implements OnChanges, OnDestroy {
  @Input() cards: InsightCard[] = [];

  currentIndex = 0;
  visible = true;
  progressPct = 0;

  private cycleTimer: ReturnType<typeof setInterval> | null = null;
  private progressTimer: ReturnType<typeof setInterval> | null = null;
  private readonly CYCLE_MS = 10000;
  private readonly PROGRESS_TICK_MS = 100;

  get card(): InsightCard {
    return this.cards[this.currentIndex] ?? this.cards[0];
  }

  ngOnChanges() {
    if (this.cards.length > 0) this.startCycle();
  }

  ngOnDestroy() { this.clearTimers(); }

  advance() {
    this.clearTimers();
    this.fadeToNext();
    this.startCycle();
  }

  private startCycle() {
    this.clearTimers();
    this.progressPct = 0;

    this.progressTimer = setInterval(() => {
      this.progressPct = Math.min(100, this.progressPct + (100 / (this.CYCLE_MS / this.PROGRESS_TICK_MS)));
    }, this.PROGRESS_TICK_MS);

    this.cycleTimer = setInterval(() => this.fadeToNext(), this.CYCLE_MS);
  }

  private fadeToNext() {
    this.visible = false;
    setTimeout(() => {
      this.currentIndex = (this.currentIndex + 1) % this.cards.length;
      this.progressPct = 0;
      this.visible = true;
    }, 520);
  }

  private clearTimers() {
    if (this.cycleTimer) { clearInterval(this.cycleTimer); this.cycleTimer = null; }
    if (this.progressTimer) { clearInterval(this.progressTimer); this.progressTimer = null; }
  }
}


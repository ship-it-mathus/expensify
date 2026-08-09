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
    <div style="position: relative; width: 100%; max-width: 320px; margin: 0 auto;">
      <canvas #canvas></canvas>
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
    if (this.chart) this.updateChart();
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
  template: `<canvas #canvas></canvas>`
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

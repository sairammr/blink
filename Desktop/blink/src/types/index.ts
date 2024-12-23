export interface BlinkStats {
  todayCount: number;
  twentyMinAvg: number;
  hourlyAvg: number;
}

export type TimeRange = 'daily' | 'weekly' | 'monthly';
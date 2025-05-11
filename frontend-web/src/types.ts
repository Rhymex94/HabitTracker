export interface Habit {
  id: number;
  name: string;
  type: 'binary' | 'quantitative';  // Adjust as per your backend enum
  target: number;
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly';  // Adjust as per your backend enum
  created_at: string;
  updated_at: string;
}
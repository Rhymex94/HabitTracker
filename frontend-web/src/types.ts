export interface Habit {
	id: number;
	name: string;
	type: "above" | "below"; // Adjust as per your backend enum
	frequency: "daily" | "weekly" | "monthly" | "yearly"; // Adjust as per your backend enum
	target: number;
	unit?: string;
	is_completed?: boolean;
	created_at: string;
	updated_at: string;
}


export interface Progress {
	id: number,
	habit_id: number,
	date: string,
	value: number,
}

/**
 * Checks if a habit is binary (simple yes/no completion).
 * Binary habits have target 0 or 1 - they're either done or not.
 * Examples: "Meditate today" (target 1), "No smoking" (target 0, BELOW type)
 */
export const isHabitBinary = (habit: Habit): boolean => {
	return habit.target === 0 || habit.target === 1;
};
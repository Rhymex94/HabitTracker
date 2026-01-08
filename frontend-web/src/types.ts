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
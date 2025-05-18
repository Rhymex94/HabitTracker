export interface Habit {
	id: number;
	name: string;
	type: "binary" | "quantitative"; // Adjust as per your backend enum
	frequency: "daily" | "weekly" | "monthly" | "yearly"; // Adjust as per your backend enum
	target: number;
	created_at: string;
	updated_at: string;
}
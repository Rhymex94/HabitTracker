import React, { useMemo } from "react";
import type { Habit, Progress } from "../types.ts";
import HabitCard from "./HabitCard.tsx";

interface HabitListProps {
	habits: Habit[];
	progress: Progress[];
}

const HabitList: React.FC<HabitListProps> = ({ habits, progress }) => {
	const habitMap = useMemo(() => {
		let habitMap: { [habit_id: number]: Habit } = {};
		for (let habit of habits) {
			habitMap[habit.id] = habit;
		}
		return habitMap;
	}, [habits]);

	const progressMap = useMemo(() => {
		if (!habits.length) return new Map();

		let progressMap = new Map<number, Progress[]>();

		for (let prog of progress) {
			if (!progressMap.has(prog.habit_id)) {
				progressMap.set(prog.habit_id, []);
			}
			let habit = habitMap[prog.habit_id];
			if (habit == undefined) {
				continue;
			}

			// Determine which progress entries we want to keep.
			let cutOffDay = new Date();
			cutOffDay.setHours(0, 0, 0, 0);

			switch (habit.frequency) {
				case "weekly": {
					// TODO: change to actual weeks, not just 7 day periods.
					cutOffDay.setDate(cutOffDay.getDate() - 7);
					break;
				}
				case "monthly": {
					// TODO: change to follow actual months, not just 30 day periods.
					cutOffDay.setDate(cutOffDay.getDate() - 30);
					break;
				}
				case "yearly": {
					// TODO: change to follow actual years, not just 365 day periods.
					cutOffDay.setDate(cutOffDay.getDate() - 365);
					break;
				}
			}

			let progDate = new Date(prog.date);
			if (progDate >= cutOffDay) {
				progressMap.get(prog.habit_id)!.push(prog);
			}
		}
		return progressMap;
	}, [habits, progress]);

	return (
		<div>
			{habits.map((habit) => (
				<HabitCard
					key={habit.id}
					habit={habit}
					progress={progressMap.get(habit.id) || []}
				/>
			))}
		</div>
	);
};

export default HabitList;

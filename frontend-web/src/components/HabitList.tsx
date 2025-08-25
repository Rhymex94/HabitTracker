import React, { useMemo } from "react";
import type { Habit, Progress } from "../types.ts";
import HabitCard from "./HabitCard.tsx";

interface HabitListProps {
	habits: Habit[];
	progress: Progress[];
	stats: Map<string, number>;
}

const HabitList: React.FC<HabitListProps> = ({ habits, progress, stats }) => {
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
			progressMap.get(prog.habit_id)!.push(prog);
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
					stats={stats.get(habit.id.toString())}
				/>
			))}
		</div>
	);
};

export default HabitList;

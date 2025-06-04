import React from 'react';
import type { Habit } from '../types.ts';
import HabitCard from './HabitCard.tsx';

interface HabitListProps {
	habits: Habit[];
	reloadHabits: () => void;
}

const HabitList: React.FC<HabitListProps> = ({ habits, ...props }) => {
	return (
		<div>
			{habits.map((habit) => (
				<HabitCard key={habit.id} habit={habit} {...props} />
			))}
		</div>
	);
};

export default HabitList;
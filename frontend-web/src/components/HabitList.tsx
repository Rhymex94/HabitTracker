import React from 'react';
import type { Habit } from '../types.ts';
import HabitCard from './HabitCard.tsx';

interface HabitListProps {
	habits: Habit[];
}

const HabitList: React.FC<HabitListProps> = ({ habits }) => {
	return (
		<div>
			{habits.map((habit) => (
				<HabitCard key={habit.id} habit={habit} />
			))}
		</div>
	);
};

export default HabitList;
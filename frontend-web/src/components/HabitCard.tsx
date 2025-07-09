import React from 'react';
import './HabitCard.css';
import type { Habit } from "../types";
import { useHabitContext } from "../context/HabitContext";

interface HabitCardProps {
	habit: Habit;
}

const HabitCard: React.FC<HabitCardProps> = ({ habit }) => {
	const { selectHabitToDelete, selectHabitToEdit, selectHabitToAddProgressTo } =
		useHabitContext();
	return (
		<div className="habit-card">
			<div className="habit-card-content">
				<h3>{habit.name}</h3>
				<p className="habit-type">{habit.type}</p>
				<p className="habit-frequency text-secondary">
					Frequency: {habit.frequency}
				</p>
				<p className="habit-target text-secondary">{habit.target}</p>
			</div>
			<div className="habit-buttons-container">
				<button
					className="button button-secondary"
					onClick={() => selectHabitToAddProgressTo(habit)}
				>
					Add Progress
				</button>
				<button
					className="button button-tertiary"
					onClick={() => selectHabitToEdit(habit)}
				>
					Edit
				</button>
				<button
					className="button button-danger"
					onClick={() => selectHabitToDelete(habit)}
				>
					Delete
				</button>
			</div>
		</div>
	);
};

export default HabitCard;
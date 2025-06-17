import React from 'react';
import './HabitCard.css';
import type { Habit } from "../types";

interface HabitCardProps {
	habit: Habit;
	selectHabitToDelete: (habit: Habit | null) => void;
	selectHabitToEdit: (habit: Habit | null) => void;
}

const HabitCard: React.FC<HabitCardProps> = ({
	habit,
	selectHabitToDelete,
	selectHabitToEdit,
}) => {
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
				<button className="button button-secondary">Add Progress</button>
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
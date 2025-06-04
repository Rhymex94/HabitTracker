import React from 'react';
import './HabitCard.css';
import type { Habit } from '../types';
import api from "../api/axios";

interface HabitCardProps {
	habit: Habit;
	reloadHabits: () => void;
}

const HabitCard: React.FC<HabitCardProps> = ({ habit, reloadHabits }) => {
	const handleDelete = async (habitId: number) => {
		try {
			await api.delete(`/habits/${habitId}`);
			reloadHabits();
		} catch (error) {
			console.error("Error deleting habit:", error);
		}
	};

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
				<button className="button button-tertiary">Edit</button>
				<button
					className="button button-danger"
					onClick={() => handleDelete(habit.id)}
				>
					Delete
				</button>
			</div>
		</div>
	);
};

export default HabitCard;
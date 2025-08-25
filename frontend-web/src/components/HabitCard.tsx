import React from 'react';
import './HabitCard.css';
import type { Habit, Progress } from "../types";
import { useHabitContext } from "../context/HabitContext";
import { FaCheck, FaFire } from "react-icons/fa";

interface HabitCardProps {
	habit: Habit;
	progress: Progress[];
	stats: number | undefined;
}

const HabitCard: React.FC<HabitCardProps> = ({ habit, progress, stats }) => {
	const { selectHabitToDelete, selectHabitToEdit, selectHabitToAddProgressTo } =
		useHabitContext();

	const getProgressDisplay = () => {
		return `${getProgress()}/${habit.target}`;
	};

	const getProgress = () => {
		// TODO: getProgress is called multiple times. Could cache the result somewhere.
		let totalValue = 0;
		for (let prog of progress) {
			totalValue += prog.value;
		}
		return totalValue;
	};

	const isHabitCompleted = () => {
		// TODO: Frontend shouldn't need to know this logic. Move to backend instead.
		if (habit.type == "above") {
			return getProgress() >= habit.target;
		}
		return getProgress() <= habit.target;
	};

	return (
		<div className="habit-card">
			<div className="habit-card-content">
				<h3>{habit.name}</h3>
				<p className="habit-type">{habit.type}</p>
				<p className="habit-frequency text-secondary">
					Frequency: {habit.frequency}
				</p>
			</div>
			<div className="progress-container">
				<label>{getProgressDisplay()}</label>
				{isHabitCompleted() && <FaCheck className="habit-check-icon" />}
			</div>
			<div className="streak-container">
				{stats !== undefined && stats !== 0 && <label>({stats})</label>}
				{stats !== undefined && stats !== 0 && (
					<FaFire className="streak-fire-icon" />
				)}
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
import React from 'react';
import './HabitCard.css';
import type { Habit, Progress } from "../types";
import { useHabitContext } from "../context/HabitContext";

interface HabitCardProps {
	habit: Habit;
	progress: Progress[];
}

const HabitCard: React.FC<HabitCardProps> = ({ habit, progress }) => {
	const { selectHabitToDelete, selectHabitToEdit, selectHabitToAddProgressTo } =
		useHabitContext();

	const getProgressDisplay = () => {
		if (habit.type == "binary") {
			return `${getBinaryProgress()}/1`;
		}
		return `${getFrequencyProgress()}/${habit.target}`;
	};

	const getBinaryProgress = () => {
		let latestDate: Date | null = null;
		let latestValue = 0;
		for (let prog of progress) {
			let progDate = new Date(prog.date);

			if (latestDate == null || latestValue == null || progDate > latestDate) {
				latestDate = progDate;
				latestValue = prog.value;
			}
		}
		return latestValue;
	};

	const getFrequencyProgress = () => {
		let totalValue = 0;
		for (let prog of progress) {
			totalValue += prog.value;
		}
		return totalValue;
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
			<div className="progress-container">
				<label>{getProgressDisplay()}</label>
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
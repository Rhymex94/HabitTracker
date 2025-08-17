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
		if (habit.type == "binary") {
			return `${getBinaryProgress()}/1`;
		}
		return `${getFrequencyProgress()}/${habit.target}`;
	};

	const getBinaryProgress = () => {
		let latestDate: Date | null = null;
		let latestId: number | null = null;
		let latestValue = 0;
		for (let prog of progress) {
			let progDate = new Date(prog.date);
			progDate.setHours(0, 0, 0, 0);

			if (latestDate == null || latestId == null) {
				latestDate = progDate;
				latestId = prog.id;
				latestValue = prog.value;
				continue;
			}

			if (progDate > latestDate || (progDate >= latestDate && prog.id > latestId)) {
				latestDate = progDate;
				latestId = prog.id;
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

	const isHabitCompleted = () => {
		if (habit.type == "binary") {
			return getBinaryProgress() == 1;
		}
		return getFrequencyProgress() >= habit.target;
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
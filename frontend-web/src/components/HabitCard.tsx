import React from 'react';
import './HabitCard.css';
import { isHabitBinary, type Habit, type Progress } from "../types";
import { useHabitContext } from "../context/HabitContext";
import { FaCheck, FaFire, FaRegSquare, FaCheckSquare } from "react-icons/fa";

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

	const getProgressPercentage = () => {
		const progressRatio = Math.min((getProgress() / habit.target) * 100, 100);

		if (habit.type === "above") {
			// ABOVE: Empty bar at 0, fills up as we reach target (blue->green)
			return progressRatio;
		} else {
			// BELOW: Full bar at 0, empties as we approach target (blue->green)
			if (habit.target === 0) {
				// For target 0, show empty bar if any progress (failure)
				return getProgress() > 0 ? 0 : 100;
			}
			return 100 - progressRatio;
		}
	};

	const isBelowHabitExceeded = () => {
		return habit.type === "below" && getProgress() > habit.target;
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
				{isHabitBinary(habit) ? (
					<div className="binary-progress">
						<div></div>
						<div className="binary-progress-content">
							{habit.is_completed ? (
								<FaCheckSquare className="habit-checkbox-icon completed" />
							) : (
								<FaRegSquare className="habit-checkbox-icon" />
							)}
							<label>{getProgressDisplay()}</label>
						</div>
						<span></span>
					</div>
				) : (
					<div className="quantitative-progress">
						<div className="progress-check-column">
							{habit.is_completed && <FaCheck className="habit-check-icon" />}
						</div>
						<div className="progress-bar-container">
							<div
								className={`progress-bar-fill ${habit.type === "below" ? "below-type" : ""}`}
								style={{ width: `${getProgressPercentage()}%` }}
							/>
							<span className={`progress-text ${isBelowHabitExceeded() ? "exceeded" : ""}`}>
								{getProgressDisplay()}
							</span>
						</div>
						<span className="progress-unit" title={habit.unit || ""}>{habit.unit || ""}</span>
					</div>
				)}
			</div>
			<div className="streak-container">
				{stats !== undefined && stats !== 0 && (
					<FaFire className="streak-fire-icon" />
				)}
				{stats !== undefined && stats !== 0 && <label>({stats})</label>}
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
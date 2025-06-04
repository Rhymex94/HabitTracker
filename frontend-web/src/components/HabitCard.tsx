import React from 'react';
import './HabitCard.css';
import type { Habit } from '../types';

interface HabitCardProps {
  habit: Habit;
}

const HabitCard: React.FC<HabitCardProps> = ({ habit }) => {
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
				<button className="button button-danger">Delete</button>
			</div>
		</div>
  );
};

export default HabitCard;
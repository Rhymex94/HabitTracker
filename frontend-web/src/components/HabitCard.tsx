import React from 'react';
import './HabitCard.css';
import type { Habit } from '../types';

interface HabitCardProps {
  habit: Habit;
}

const HabitCard: React.FC<HabitCardProps> = ({ habit }) => {
  return (
    <div className="habit-card">
      <h3>{habit.name}</h3>
      <p className="habit-type">{habit.type}</p>
      <p className="habit-frequency text-secondary">Frequency: {habit.frequency}</p>
    </div>
  );
};

export default HabitCard;
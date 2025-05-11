import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import type { Habit } from '../types.ts';

const HabitList: React.FC = () => {
  const [habits, setHabits] = useState<Habit[]>([]);

  useEffect(() => {
    const fetchHabits = async () => {
      try {
        const response = await api.get('/habits');
        setHabits(response.data);
      } catch (error) {
        console.error('Error fetching habits:', error);
      }
    };

    fetchHabits();
  }, []);

  return (
    <div>
      <h1>Habit List</h1>
      <ul>
        {habits.map((habit) => (
          <li key={habit.id}>{habit.name} - {habit.type}</li>
        ))}
      </ul>
    </div>
  );
};

export default HabitList;
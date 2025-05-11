import React from 'react';
import HabitList from '../components/HabitList';

const Home: React.FC = () => {
  return (
    <div>
      <h1>Welcome to Habit Tracker!</h1>
      <HabitList />
    </div>
  );
};

export default Home;
import React, { useState, useEffect } from "react";
import type { Habit } from "./types";
import "../styles.css"
import api from "./api/axios";
import HabitList from "./components/HabitList";

const App: React.FC = () => {
	const [habits, setHabits] = useState<Habit[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		api.get("/habits")
			.then((response) => {
				setHabits(response.data);
				setError(null);
			})
			.catch((err) => {
				setError("Failed to fetch habits");
				console.log("Error fetching habits", err);
			})
			.finally(() => {
				setLoading(false);
			});
	}, []);

	return (
    <div>
      <h1>Habit Tracker</h1>
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      {!loading && !error && <HabitList habits={habits} />}
    </div>
	);
};

export default App;

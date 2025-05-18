import React, { useState, useEffect } from "react";
import type { Habit } from "./types";
import "../styles.css"
import api from "./api/axios";
import HabitList from "./components/HabitList";
import AddHabitModal from "./components/AddHabitModal";

const App: React.FC = () => {
	const [habits, setHabits] = useState<Habit[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [isModalOpen, setIsModalOpen] = useState(false);

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

	const handleAddHabit = async (newHabit: Omit<Habit, "id">) => {
		try {
			const response = await api.post("/habits", newHabit);
			setHabits([...habits, response.data]);
		} catch (err) {
			setError("Failed to add habit");
			console.error("Error adding habit:", err);
		}
	};

	return (
		<div>
			<header className="header">
				<h1>Habit Tracker</h1>
				<button className="add-button" onClick={() => setIsModalOpen(true)}>
					Add Habit
				</button>
			</header>
			{loading && <p>Loading...</p>}
			{error && <p>{error}</p>}
			{!loading && !error && <HabitList habits={habits} />}
			<AddHabitModal
				isOpen={isModalOpen}
				onClose={() => setIsModalOpen(false)}
				onSubmit={handleAddHabit}
			/>
		</div>
	);
};

export default App;

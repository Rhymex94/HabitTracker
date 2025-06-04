import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import type { Habit } from "../types";
import api from "../api/axios";
import HabitList from "./HabitList";
import AddHabitModal from "./AddHabitModal";

const Dashboard: React.FC = () => {
	const { logout } = useAuth();
	const [habits, setHabits] = useState<Habit[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [isModalOpen, setIsModalOpen] = useState(false);

	//TODO: Could replace the arrow function here with reloadHabits?
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

	const reloadHabits = async () => {
		try {
			const response = await api.get("/habits");
			setHabits(response.data);
			setError(null);
		} catch (err) {
			setError("Failed to fetch habits");
			console.log("Error fetching habits", err);
		}
	};

	const handleAddHabit = async (
		newHabit: Omit<Habit, "id" | "created_at" | "updated_at">
	) => {
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
				<div className="header-content">
					<h1>Habit Tracker</h1>
					<div className="header-actions">
						<button
							className="add-button"
							onClick={() => setIsModalOpen(true)}
						>
							Add Habit
						</button>
						<button className="button button-tertiary" onClick={logout}>
							Logout
						</button>
					</div>
				</div>
			</header>
			{loading && <p>Loading...</p>}
			{error && <p className="error-message">{error}</p>}
			{!loading && !error && (
				<HabitList habits={habits} reloadHabits={reloadHabits} />
			)}
			<AddHabitModal
				isOpen={isModalOpen}
				onClose={() => setIsModalOpen(false)}
				onSubmit={handleAddHabit}
			/>
		</div>
	);
};

export default Dashboard;

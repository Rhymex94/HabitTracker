import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import type { Habit } from "../types";
import api from "../api/axios";
import HabitList from "./HabitList";
import AddHabitModal from "./AddHabitModal";
import DeleteHabitModal from "./DeleteHabitModal";
import EditHabitModal from "./EditHabitModal";

import { HabitProvider } from "../context/HabitContext";

const Dashboard: React.FC = () => {
	const { logout } = useAuth();
	const [habits, setHabits] = useState<Habit[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [isAddModalOpen, setIsAddModalOpen] = useState(false);
	const [habitToDelete, setHabitToDelete] = useState<Habit | null>(null);
	const [habitToEdit, setHabitToEdit] = useState<Habit | null>(null);

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

	const handleEditHabit = async (
		habitId: number,
		habit: Omit<Habit, "id" | "created_at" | "updated_at">
	) => {
		try {
			await api.patch(`/habits/${habitId}`, habit);
			setHabitToEdit(null);
			reloadHabits();
		} catch (err) {
			setError("Failed to edit habit");
			console.error("Error editing habit:", err);
		}
	};

	const handleDeleteHabit = async (habitId: number) => {
		try {
			await api.delete(`/habits/${habitId}`);
			setHabitToDelete(null);
			reloadHabits();
		} catch (error) {
			console.error("Error deleting habit:", error);
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
							onClick={() => setIsAddModalOpen(true)}
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
				<HabitProvider
					selectHabitToDelete={setHabitToDelete}
					selectHabitToEdit={setHabitToEdit}
				>
					<HabitList habits={habits} />
				</HabitProvider>
			)}
			<AddHabitModal
				isOpen={isAddModalOpen}
				onClose={() => setIsAddModalOpen(false)}
				onSubmit={handleAddHabit}
			/>
			{habitToDelete && (
				<DeleteHabitModal
					habit={habitToDelete}
					onClose={() => setHabitToDelete(null)}
					onSubmit={handleDeleteHabit}
				/>
			)}
			{habitToEdit && (
				<EditHabitModal
					habit={habitToEdit}
					onClose={() => setHabitToEdit(null)}
					onSubmit={handleEditHabit}
				/>
			)}
		</div>
	);
};

export default Dashboard;

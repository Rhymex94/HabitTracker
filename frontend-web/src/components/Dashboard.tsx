import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import type { Habit, Progress } from "../types";
import api from "../api/axios";
import HabitList from "./HabitList";
import AddHabitModal from "./AddHabitModal";
import DeleteHabitModal from "./DeleteHabitModal";
import EditHabitModal from "./EditHabitModal";

import { HabitProvider } from "../context/HabitContext";
import AddProgressModal from "./AddProgressModal";
import MarkHabitCompleteModal from "./MarkHabitCompleteModal";

const Dashboard: React.FC = () => {
	const { logout } = useAuth();
	const [habits, setHabits] = useState<Habit[]>([]);
	const [progress, setProgress] = useState<Progress[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [isAddModalOpen, setIsAddModalOpen] = useState(false);
	const [habitToDelete, setHabitToDelete] = useState<Habit | null>(null);
	const [habitToEdit, setHabitToEdit] = useState<Habit | null>(null);
	const [habitToAddProgressTo, setHabitToAddProgressTo] = useState<Habit | null>(null);

	useEffect(() => {
		Promise.all([reloadHabits(), reloadProgress()])
			.then(() => {
				setError(null);
			})
			.catch((err) => {
				setError("Failed to fetch habits or progress");
				console.error("Error fetching data", err);
			})
			.finally(() => {
				setLoading(false);
			});
	}, []);

	const reloadHabits = async () => {
		return api
			.get("/habits")
			.then((response) => {
				setHabits(response.data);
			})
			.catch((err) => {
				console.error("Failed to load habits", err);
				throw err;
			});
	};

	const reloadProgress = async () => {
		return api
			.get("/progress")
			.then((response) => {
				setProgress(response.data);
			})
			.catch((err) => {
				setError("Failed to load progress");
				throw err;
			});
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
			reloadProgress();
		} catch (error) {
			console.error("Error deleting habit:", error);
		}
	};

	const handleAddProgress = async (habitId: number, progress: number) => {
		try {
			await api.post("/progress", { habit_id: habitId, value: progress });
			setHabitToAddProgressTo(null);
			reloadProgress();
		} catch (error) {
			console.error("Error adding progress to habit:", error);
		}
	};

	const isHabitBinary = (habit: Habit) => {
		if (habit.type == "binary") {
			return true;
		}
		return false;
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
					selectHabitToAddProgressTo={setHabitToAddProgressTo}
				>
					{habits && <HabitList habits={habits} progress={progress} />}
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
			{habitToAddProgressTo && !isHabitBinary(habitToAddProgressTo) && (
				<AddProgressModal
					habit={habitToAddProgressTo}
					onClose={() => setHabitToAddProgressTo(null)}
					onSubmit={handleAddProgress}
				/>
			)}
			{habitToAddProgressTo && isHabitBinary(habitToAddProgressTo) && (
				<MarkHabitCompleteModal
					habit={habitToAddProgressTo}
					onClose={() => setHabitToAddProgressTo(null)}
					onSubmit={handleAddProgress}
				/>
			)}
		</div>
	);
};

export default Dashboard;

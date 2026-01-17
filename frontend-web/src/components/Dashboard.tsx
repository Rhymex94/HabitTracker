import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { isHabitBinary, type Habit, type Progress } from "../types";
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
	const [stats, setStats] = useState<Map<string, number>>(new Map());
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [isAddModalOpen, setIsAddModalOpen] = useState(false);
	const [habitToDelete, setHabitToDelete] = useState<Habit | null>(null);
	const [habitToEdit, setHabitToEdit] = useState<Habit | null>(null);
	const [habitToAddProgressTo, setHabitToAddProgressTo] = useState<Habit | null>(null);

	useEffect(() => {
		Promise.all([reloadHabits(), reloadProgress(), reloadStats()])
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
				setHabits(response.data.data);
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
				setProgress(response.data.data);
			})
			.catch((err) => {
				setError("Failed to load progress");
				throw err;
			});
	};

	const reloadStats = async () => {
		return api
			.get("/stats")
			.then((response) => {
				setStats(new Map(Object.entries(response.data.data)));
			})
			.catch((err) => {
				setError("Failed to load stats");
				throw err;
			});
	};

	const handleAddHabit = async (
		newHabit: Omit<Habit, "id" | "created_at" | "updated_at">
	) => {
		try {
			const response = await api.post("/habits", newHabit);
			setHabits([...habits, response.data.data]);
		} catch (err) {
			setError("Failed to add habit");
			console.error("Error adding habit:", err);
		}
	};

	const handleEditHabit = async (
		habitId: number,
		updatedFields: Omit<Habit, "id" | "created_at" | "updated_at">
	) => {
		try {
			await api.patch(`/habits/${habitId}`, updatedFields);
			// Optimistic update: merge updated fields into existing habit
			setHabits((prevHabits) =>
				prevHabits.map((h) =>
					h.id === habitId ? { ...h, ...updatedFields } : h
				)
			);
			setHabitToEdit(null);
		} catch (err) {
			setError("Failed to edit habit");
			console.error("Error editing habit:", err);
		}
	};

	const handleDeleteHabit = async (habitId: number) => {
		try {
			await api.delete(`/habits/${habitId}`);
			// Optimistic update: remove habit from local state
			setHabits((prevHabits) => prevHabits.filter((h) => h.id !== habitId));
			// Remove related progress entries
			setProgress((prevProgress) =>
				prevProgress.filter((p) => p.habit_id !== habitId)
			);
			// Remove the habit's streak from stats
			setStats((prevStats) => {
				const newStats = new Map(prevStats);
				newStats.delete(String(habitId));
				return newStats;
			});
			setHabitToDelete(null);
		} catch (error) {
			console.error("Error deleting habit:", error);
		}
	};

	const handleAddProgress = async (habitId: number, value: number) => {
		try {
			const response = await api.post("/progress", {
				habit_id: habitId,
				value: value,
			});
			// Add new progress entry to local state from response
			setProgress((prevProgress) => [...prevProgress, response.data.data]);
			setHabitToAddProgressTo(null);
			// Still need to reload habits (for is_completed) and stats (for streaks)
			// as these are calculated server-side
			reloadHabits();
			reloadStats();
		} catch (error) {
			console.error("Error adding progress to habit:", error);
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
					selectHabitToAddProgressTo={setHabitToAddProgressTo}
				>
					{habits && (
						<HabitList habits={habits} progress={progress} stats={stats} />
					)}
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

import React, { useState } from "react";
import type { Habit } from "../types";

interface AddHabitModalProps {
	isOpen: boolean;
	onClose: () => void;
	onSubmit: (habit: Omit<Habit, "id" | "created_at" | "updated_at">) => void;
}

const AddHabitModal: React.FC<AddHabitModalProps> = ({ isOpen, onClose, onSubmit }) => {
	const [name, setName] = useState("");
	const [type, setType] = useState<"above" | "below">("above");
	const [frequency, setFrequency] = useState<"daily" | "weekly" | "monthly" | "yearly">(
		"daily"
	);
	const [target, setTarget] = useState("1");

	if (!isOpen) return null;

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		onSubmit({
			name,
			type,
			frequency,
			target: parseInt(target, 10),
		});
		setName("");
		setType("above");
		setFrequency("daily");
		setTarget("1");
		onClose();
	};

	return (
		<div className="modal-overlay">
			<div className="modal-content">
				<h2>Add New Habit</h2>
				<form onSubmit={handleSubmit}>
					<div className="form-group">
						<label htmlFor="name">Habit Name</label>
						<input
							type="text"
							id="name"
							value={name}
							onChange={(e) => setName(e.target.value)}
							required
						/>
					</div>
					<div className="form-group">
						<label htmlFor="type">Type</label>
						<select
							id="type"
							value={type}
							onChange={(e) =>
								setType(e.target.value as "above" | "below")
							}
						>
							<option value="above">Above</option>
							<option value="below">Below</option>
						</select>
					</div>
					<div className="form-group">
						<label htmlFor="frequency">Frequency</label>
						<select
							id="frequency"
							value={frequency}
							onChange={(e) =>
								setFrequency(
									e.target.value as
										| "daily"
										| "weekly"
										| "monthly"
										| "yearly"
								)
							}
						>
							<option value="daily">Daily</option>
							<option value="weekly">Weekly</option>
							<option value="monthly">Monthly</option>
							<option value="yearly">Yearly</option>
						</select>
					</div>
					<div className="form-group">
						<label htmlFor="target">Target Value</label>
						<input
							type="number"
							id="target"
							min="0"
							value={target}
							onChange={(e) => setTarget(e.target.value)}
							required
						/>
					</div>
					<div className="modal-actions">
						<button
							type="button"
							className="button button-secondary"
							onClick={onClose}
						>
							Cancel
						</button>
						<button type="submit" className="add-button">
							Add Habit
						</button>
					</div>
				</form>
			</div>
		</div>
	);
};

export default AddHabitModal;

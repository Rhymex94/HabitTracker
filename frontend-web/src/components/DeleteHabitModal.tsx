import React from "react";
import type { Habit } from "../types";

interface DeleteHabitModalProps {
	habit: Habit;
	onClose: () => void;
	onSubmit: (id: number) => void;
}

const DeleteHabitModal: React.FC<DeleteHabitModalProps> = ({
	habit,
	onClose,
	onSubmit,
}) => {
	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		onSubmit(habit.id);
	};

	return (
		<div className="modal-overlay">
			<div className="modal-content">
				<h2>Delete Habit</h2>
				<p>Are you sure you want to delete habit {habit.name}?</p>
				<form onSubmit={handleSubmit}>
					<div className="modal-actions">
						<button
							type="button"
							className="button button-secondary"
							onClick={onClose}
						>
							Cancel
						</button>
						<button type="submit" className="button button-danger">
							Delete
						</button>
					</div>
				</form>
			</div>
		</div>
	);
};

export default DeleteHabitModal;

import { useState } from "react";
import type { Habit } from "../types";

interface AddProgressModalProps {
	habit: Habit;
	onClose: () => void;
	onSubmit: (habitId: number, progress: number) => void;
}

const AddProgressModal: React.FC<AddProgressModalProps> = ({
	habit,
	onClose,
	onSubmit,
}) => {
	const [progress, setProgress] = useState("");

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		onSubmit(habit.id, parseFloat(progress));
		onClose();
	};

	return (
		<div className="modal-overlay">
			<div className="modal-content">
				<h2>Add Progress</h2>
				<form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="">Progress</label>
                        <input
                            type="number"
                            id="progress"
                            value={progress}
                            onChange={(e) => setProgress(e.target.value)}
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
						<button type="submit" className="add-progress">
							Add Progress
						</button>
                    </div>
				</form>
			</div>
		</div>
	);
};

export default AddProgressModal;
import React, { useState } from "react";
import type { Habit } from "../types";

interface EditHabitModalProps {
    habit: Habit;
    onClose: () => void;
    onSubmit: (habitId: number, habit: Omit<Habit, "id" | "created_at" | "updated_at">) => void;
}

const EditHabitModal: React.FC<EditHabitModalProps> = ({ habit, onClose, onSubmit }) => {
    const [name, setName] = useState(habit.name);
    const [type, setType] = useState<"binary" | "quantitative">(habit.type);
    const [frequency, setFrequency] = useState<"daily" | "weekly" | "monthly" | "yearly">(
        habit.frequency
    );
    const [target, setTarget] = useState(habit.target.toString());

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(habit.id, {
            name,
            type,
            frequency,
            target: parseInt(target, 10),
        });
        onClose();
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>Edit Habit</h2>
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
                                setType(e.target.value as "binary" | "quantitative")
                            }
                        >
                            <option value="binary">Binary</option>
                            <option value="quantitative">Quantitative</option>
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
                            min="1"
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
                            Save Habit
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditHabitModal;

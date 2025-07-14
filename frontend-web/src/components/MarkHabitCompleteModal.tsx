import type { Habit } from "../types";
import api from "../api/axios";
import { useEffect, useState } from "react";

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
    const [completed, setCompleted] = useState<boolean>(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        let newValue = 0;
        if (!completed) {
            newValue = 1;
        }

        onSubmit(habit.id, newValue);
        onClose();
    };


    useEffect(() => {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, "0");
        const dd = String(today.getDate()).padStart(2, "0");

        const todayString = `${yyyy}-${mm}-${dd}`;
        const url = `/progress?habit_id=${habit.id}&start_date=${todayString}&end_date=${todayString}`;

        api.get(url)
            .then((response) => {
                const entries = response.data;
                let latestId = 0;
                let latestValue = 0;
                for (let entry of entries) {
                    if (entry.id > latestId) {
                        latestId = entry.id;
                        latestValue = entry.value;
                    }
                }
                let isComplete = latestValue == 1;
                setCompleted(isComplete);
            })
            .catch((err) => {
                console.log("Error fetching progress entries:", err);
            })
        }, []);

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <h2>Mark Complete</h2>
                <form onSubmit={handleSubmit}>
                    <div className="modal-actions">
                        <button
                            type="button"
                            className="button button-secondary"
                            onClick={onClose}
                        >
                            Cancel
                        </button>
                        <button type="submit" className={completed ? "button button-danger" : "button button-primary"}>
                            Add Progress
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddProgressModal;
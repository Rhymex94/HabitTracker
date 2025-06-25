import React, { createContext, useContext } from 'react';
import type { Habit } from "../types";

type HabitContextType = {
    selectHabitToDelete: (habit: Habit | null) => void;
    selectHabitToEdit: (habit: Habit | null) => void;
}

const HabitContext = createContext<HabitContextType | undefined>(undefined);

export const useHabitContext = () => {
    const context = useContext(HabitContext);
    if (!context) throw new Error('useHabitContext must be used within a HabitProvider');
    return context;
};

export const HabitProvider = ({
  children,
  selectHabitToDelete,
  selectHabitToEdit,
}: {
  children: React.ReactNode;
  selectHabitToDelete: (habit: Habit | null) => void;
  selectHabitToEdit: (habit: Habit | null) => void;
}) => (
  <HabitContext.Provider value={{ selectHabitToDelete, selectHabitToEdit }}>
    {children}
  </HabitContext.Provider>
);
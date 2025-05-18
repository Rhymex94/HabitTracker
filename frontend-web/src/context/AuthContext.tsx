import React, { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

interface AuthContextType {
	isAuthenticated: boolean;
	userId: string | null;
	logout: () => void;
	checkAuth: () => Promise<boolean>;
	isLoading: boolean;
	login: (token: string, userId: string, rememberMe: boolean) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
	const context = useContext(AuthContext);
	if (!context) {
		throw new Error("useAuth must be used within an AuthProvider");
	}
	return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const [userId, setUserId] = useState<string | null>(null);
	const [isLoading, setIsLoading] = useState(true);
	const navigate = useNavigate();

	const getStorage = () => {
		// Check if token exists in localStorage first, then sessionStorage
		const localToken = localStorage.getItem("token");
		if (localToken) return localStorage;
		return sessionStorage;
	};

	const login = (token: string, userId: string, rememberMe: boolean) => {
		const storage = rememberMe ? localStorage : sessionStorage;
		storage.setItem("token", token);
		storage.setItem("userId", userId);
		api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
		setIsAuthenticated(true);
		setUserId(userId);
	};

	const checkAuth = async () => {
		const storage = getStorage();
		const token = storage.getItem("token");
		const storedUserId = storage.getItem("userId");

		if (!token || !storedUserId) {
			setIsAuthenticated(false);
			setUserId(null);
			return false;
		}

		try {
			// Add token to default headers
			api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
			// Verify token with backend
			await api.get("/auth/verify");
			setIsAuthenticated(true);
			setUserId(storedUserId);
			return true;
		} catch (err) {
			logout();
			return false;
		}
	};

	const logout = () => {
		localStorage.removeItem("token");
		localStorage.removeItem("userId");
		sessionStorage.removeItem("token");
		sessionStorage.removeItem("userId");
		delete api.defaults.headers.common["Authorization"];
		setIsAuthenticated(false);
		setUserId(null);
		navigate("/login");
	};

	useEffect(() => {
		const initializeAuth = async () => {
			try {
				const storage = getStorage();
				const token = storage.getItem("token");
				if (token) {
					api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
				}
				await checkAuth();
			} catch (error) {
				console.error("Auth initialization error:", error);
			} finally {
				setIsLoading(false);
			}
		};

		initializeAuth();
	}, []);

	// Set up an interceptor to handle 401 responses
	useEffect(() => {
		const interceptor = api.interceptors.response.use(
			(response) => response,
			(error) => {
				if (error.response?.status === 401) {
					logout();
				}
				return Promise.reject(error);
			}
		);

		return () => {
			api.interceptors.response.eject(interceptor);
		};
	}, []);

	if (isLoading) {
		return <div>Loading...</div>;
	}

	return (
		<AuthContext.Provider
			value={{ isAuthenticated, userId, logout, checkAuth, isLoading, login }}
		>
			{children}
		</AuthContext.Provider>
	);
};

export default AuthContext;

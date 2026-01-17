import React, { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

interface AuthContextType {
	isAuthenticated: boolean;
	logout: () => void;
	checkAuth: () => Promise<boolean>;
	isLoading: boolean;
	login: (token: string, rememberMe: boolean) => void;
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
	const [isLoading, setIsLoading] = useState(true);
	const navigate = useNavigate();

	const getStorage = () => {
		// Check if token exists in localStorage first, then sessionStorage
		const localToken = localStorage.getItem("token");
		if (localToken) return localStorage;
		return sessionStorage;
	};

	const login = (token: string, rememberMe: boolean) => {
		const storage = rememberMe ? localStorage : sessionStorage;
		storage.setItem("token", token);
		api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
		setIsAuthenticated(true);
	};

	const checkAuth = async () => {
		const storage = getStorage();
		const token = storage.getItem("token");

		if (!token) {
			setIsAuthenticated(false);
			return false;
		}

		try {
			// Add token to default headers
			api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
			// Verify token with backend
			await api.get("/auth/verify");
			setIsAuthenticated(true);
			return true;
		} catch (err) {
			logout();
			return false;
		}
	};

	const logout = () => {
		localStorage.removeItem("token");
		sessionStorage.removeItem("token");
		delete api.defaults.headers.common["Authorization"];
		setIsAuthenticated(false);
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
			value={{ isAuthenticated, logout, checkAuth, isLoading, login }}
		>
			{children}
		</AuthContext.Provider>
	);
};

export default AuthContext;

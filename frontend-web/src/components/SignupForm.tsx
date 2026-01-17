import React, { useState } from "react";
import { useNavigate, Link, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api/axios";

const SignupForm: React.FC = () => {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const navigate = useNavigate();
	const { isAuthenticated, login } = useAuth();

	// If user is already authenticated, redirect to home
	if (isAuthenticated) {
		return <Navigate to="/" replace />;
	}

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setError(null);

		// Only validate password confirmation on frontend (not sent to backend)
		if (password !== confirmPassword) {
			setError("Passwords do not match");
			return;
		}

		try {
			const response = await api.post("/auth/signup", { username, password });

			// Use the new login function from context (default to rememberMe = true for new signups)
			login(response.data.data.token, response.data.data.user_id.toString(), true);

			// Navigate to home page
			navigate("/", { replace: true });
		} catch (err: any) {
			// Handle rate limiting
			if (err.response?.status === 429) {
				setError("Too many signup attempts. Please try again later.");
				return;
			}
			// Display validation errors from backend
			setError(err.response?.data?.message || "Failed to create account");
		}
	};

	return (
		<div className="auth-container">
			<div className="auth-form">
				<h2>Sign Up</h2>
				{error && <div className="error-message">{error}</div>}
				<form onSubmit={handleSubmit}>
					<div className="form-group">
						<label htmlFor="username">Username</label>
						<input
							type="text"
							id="username"
							value={username}
							onChange={(e) => setUsername(e.target.value)}
							required
						/>
					</div>
					<div className="form-group">
						<label htmlFor="password">Password</label>
						<input
							type="password"
							id="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							required
						/>
					</div>
					<div className="form-group">
						<label htmlFor="confirmPassword">Confirm Password</label>
						<input
							type="password"
							id="confirmPassword"
							value={confirmPassword}
							onChange={(e) => setConfirmPassword(e.target.value)}
							required
						/>
					</div>
					<button type="submit" className="button">
						Sign Up
					</button>
				</form>
				<p className="auth-link">
					Already have an account? <Link to="/login">Login</Link>
				</p>
			</div>
		</div>
	);
};

export default SignupForm;

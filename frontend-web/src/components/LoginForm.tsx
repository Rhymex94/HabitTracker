import React, { useState } from "react";
import { useNavigate, Link, useLocation, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api/axios";

interface LocationState {
	from: {
		pathname: string;
	};
}

const LoginForm: React.FC = () => {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [rememberMe, setRememberMe] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const navigate = useNavigate();
	const location = useLocation();
	const { isAuthenticated, login } = useAuth();

	// If user is already authenticated, redirect to home
	if (isAuthenticated) {
		return <Navigate to="/" replace />;
	}

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setError(null);

		try {
			const response = await api.post("/auth/login", { username, password });

			// Use the new login function from context
			login(response.data.data.token, rememberMe);

			// Get the redirect path from location state, or default to "/"
			const from = (location.state as LocationState)?.from?.pathname || "/";
			navigate(from, { replace: true });
		} catch (err: any) {
			// Handle rate limiting
			if (err.response?.status === 429) {
				setError("Too many login attempts. Please try again in a minute.");
				return;
			}
			setError("Invalid username or password");
		}
	};

	return (
		<div className="auth-container">
			<div className="auth-form">
				<h2>Login</h2>
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
					<div className="form-group checkbox-group">
						<label>
							<input
								type="checkbox"
								checked={rememberMe}
								onChange={(e) => setRememberMe(e.target.checked)}
							/>
							Remember me
						</label>
					</div>
					<button type="submit" className="button">
						Login
					</button>
				</form>
				<p className="auth-link">
					Don't have an account? <Link to="/signup">Sign up</Link>
				</p>
			</div>
		</div>
	);
};

export default LoginForm;

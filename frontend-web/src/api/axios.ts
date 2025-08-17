import axios from 'axios';

const baseUrl = (import.meta.env.VITE_API_URL ?? "") + "/api";

const api = axios.create({
	baseURL: baseUrl,
	headers: {
		"Content-Type": "application/json",
	},
	withCredentials: true,
});

export default api;
import axios from "axios";


const API = axios.create({
  // baseURL: "http://localhost:8000/app/v1",
  baseURL: "https://clockwork-backend-9q5v.onrender.com/app/v1",
  headers: { "Content-Type": "application/json" }
});

export default API;

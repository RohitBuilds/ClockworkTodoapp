import axios from "axios";


const API = axios.create({
  baseURL: "https://clockwork-backend-9q5v.onrender.com/app/v1",
  withCredentials: true, 
  headers: { "Content-Type": "application/json" }
});

export default API;

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import API from "../api";
import "../App.css";

const Login = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const [serverError, setServerError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (data) => {
  setLoading(true);
  setServerError("");

  try {
    const response = await API.post("/signin", data);

    // save token and userId
    localStorage.setItem("token", response.data.access_token || "dummy-token");
    localStorage.setItem("userId", response.data.user_id);

    navigate("/dashboard"); // redirect to dashboard
  } catch (error) {
    setServerError(
      error.response?.data?.detail || "Invalid email or password"
    );
  } finally {
    setLoading(false);
  }
}; 
  return (
    <div className="auth-wrapper">
      <div className="auth-card">

        <h2 className="auth-title">Welcome Back</h2>
        <p className="auth-subtitle">Login to continue</p>

        {serverError && <p className="auth-error">{serverError}</p>}

        <form onSubmit={handleSubmit(onSubmit)}>

          <div className="auth-input-group">
            <input
              type="email"
              placeholder="Email"
              {...register("email", {
                required: "Email is required",
                pattern: {
                  value: /^\S+@\S+\.\S+$/,
                  message: "Invalid email format",
                },
              })}
            />
            {errors.email && <p className="auth-validation">{errors.email.message}</p>}
          </div>

          <div className="auth-input-group">
            <input
              type="password"
              placeholder="Password"
              {...register("password", {
                required: "Password is required",
                minLength: { value: 6, message: "Minimum 6 characters required" },
              })}
            />
            {errors.password && <p className="auth-validation">{errors.password.message}</p>}
          </div>

          <button className="auth-button" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>

        </form>

        <p className="auth-footer">
          Don't have an account?
          <Link to="/signup" className="auth-link"> Sign Up</Link>
        </p>

      </div>
    </div>
  );
};

export default Login;

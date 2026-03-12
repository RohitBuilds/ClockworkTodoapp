import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import API from "../api"; 
import { Link } from "react-router-dom";
import "../App.css";

const Signup = () => {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const [serverError, setServerError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    setLoading(true);
    setServerError("");

    try {
      // POST request to backend signup endpoint
      const response = await API.post("/signup", data);
      
      navigate("/"); // redirect to login page
    } 
    catch (error) {
       console.error("Signup error:", error);

       const errData = error?.response?.data?.detail || error?.message || "Signup failed. Try again.";

        // Make sure serverError is a string or array, not a raw object
        setServerError(errData);
     }

    finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">

        <h2 className="auth-title">Create Account</h2>
        <p className="auth-subtitle">Start your journey</p>

        {serverError && <p className="auth-error">{serverError}</p>}

        <form onSubmit={handleSubmit(onSubmit)}>

          <div className="auth-input-group">
            <input
              type="text"
              placeholder="Full Name"
              {...register("username", { required: "Name is required" })}
            />
          </div>

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
            {loading ? "Creating..." : "Sign Up"}
          </button>

        </form>

        <p className="auth-footer">
          Already have an account?
          <Link to="/" className="auth-link"> Login</Link>
        </p>

      </div>
    </div>
  );
};
export default Signup;
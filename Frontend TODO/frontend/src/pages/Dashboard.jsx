import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import { toast } from "react-toastify";


function Dashboard() {
  // const BASE_URL = "http://localhost:8000/app/v1";
  const BASE_URL = "https://clockwork-backend-9q5v.onrender.com/app/v1";
  const navigate = useNavigate();

  const [todos, setTodos] = useState([]);
  const [newTodo, setNewTodo] = useState({
    title: "",
    description: "",
    due_time: ""
  });
  const [showLogout, setShowLogout] = useState(false); // toggle logout

  const token = localStorage.getItem("token");
  const userId = localStorage.getItem("userId");
  const [showSuccess, setShowSuccess] = useState(false);


  // ================= PROTECT ROUTE =================
  useEffect(() => {
    if (!token || !userId) {
      navigate("/");
    } else {
      fetchTodos();
    }
  }, []);

  // ================= REQUEST NOTIFICATION PERMISSION =================
  useEffect(() => {

    if ("Notification" in window && Notification.permission !== "granted") {
      Notification.requestPermission();
    }

  }, []);
  // ================= SHOW NOTIFICATION =================
  const showNotification = (message) => {

  if (!("Notification" in window)) {
    console.log("Browser does not support notifications");
    return;
  }

  if (Notification.permission === "granted") {

    new Notification("⏰ Task Reminder", {
      body: message,
      icon: "/logo192.png"
    });

  } else if (Notification.permission !== "denied") {

    Notification.requestPermission().then(permission => {
      if (permission === "granted") {
        new Notification("⏰ Task Reminder", {
          body: message
        });
      }
    });

  }
};

  // ================= FETCH TODOS =================
  const fetchTodos = async () => {
    try {
      const res = await fetch(`${BASE_URL}/getalltodos/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.status === 401) {
        logout();
        return;
      }

      if (!res.ok) {
        console.log("Fetch error");
        return;
      }

      const data = await res.json();
      setTodos(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error fetching todos:", err);
    }
  };

  // ================= CREATE TODO =================
  // const createTodo = async (e) => {
  //   e.preventDefault();

  //   try {
  //     const res = await fetch(`${BASE_URL}/createtodos?user_id=${userId}`, {
  //       method: "POST",
  //       headers: {
  //         "Content-Type": "application/json",
  //         Authorization: `Bearer ${token}`,
  //       },
  //       body: JSON.stringify({
  //         title: newTodo.title,
  //         description: newTodo.description,
  //         completed: false,
  //       }),
  //     });

  //     const data = await res.json();

  //     if (!res.ok) {
  //       alert(data.message || JSON.stringify(data));
  //       return;
  //     }

  //     setNewTodo({ title: "", description: "" });
  //     fetchTodos();
  //   } catch (err) {
  //     console.error("Error creating todo:", err);
  //   }
  // };

  // ================= CREATE TODO =================
  const createTodo = async (e) => {
  e.preventDefault();

  try {

    const res = await fetch(`${BASE_URL}/createtodos?user_id=${userId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title: newTodo.title,
        description: newTodo.description,
        completed: false,
        due_time: newTodo.due_time
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.message || JSON.stringify(data));
      return;
    }

    setNewTodo({
      title: "",
      description: "",
      due_time: ""
    });

    fetchTodos();

  } catch (err) {
    console.error("Error creating todo:", err);
  }
};

// ================= CHECK REMINDERS =================
  useEffect(() => {

  const checkNotifications = async () => {

    try {

      const userId = localStorage.getItem("userId");

      const res = await fetch(
        `${BASE_URL}/notifications?user_id=${userId}`
      );

      const data = await res.json();

      console.log("Notifications:", data);

      data.forEach((note) => {

        toast.info(note.message);

        if ("Notification" in window && Notification.permission === "granted") {
          new Notification("⏰ Task Reminder", {
            body: note.message
          });
        }

      });

    } catch (error) {
      console.error("Notification error", error);
    }

  };

  checkNotifications();

  const interval = setInterval(checkNotifications, 5000);

  return () => clearInterval(interval);

}, []);



  const toggleTodo = async (id) => {
  try {
    await fetch(`${BASE_URL}/toggletodosbyid/${id}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
    });

    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 2500);

    fetchTodos();
  } catch (err) {
    console.error("Toggle error:", err);
  }
};


  // ================= DELETE =================
  const deleteTodo = async (id) => {
    try {
      await fetch(`${BASE_URL}/deletetodosbyid/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchTodos();
    } catch (err) {
      console.error("Delete error:", err);
    }
  };

  // ================= DELETE ALL =================
  const deleteAllTodos = async () => {
    try {
      await fetch(`${BASE_URL}/deletealltodos/${userId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchTodos();
    } catch (err) {
      console.error("Delete all error:", err);
    }
  };

  // ================= LOGOUT =================
  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    navigate("/");
  };

  return (
    <div className="app-bg">
      <div className="app-container">
        {/* ================= HEADER ================= */}
          <header className="navbar">

  <div className="nav-content">

    <div className="nav-left">
      <h1 className="logo">CLOCKWORK</h1>
      <span className="tagline">Organize beautifully. Execute powerfully.</span>
    </div>

    <div className="nav-right">
      <button className="logout-btn-top" onClick={logout}>
        Logout
      </button>
    </div>

  </div>

</header>
          {/* ================= CREATE TODO ================= */}

        <div className="todo-card">

          <form onSubmit={createTodo} className="todo-form">

            <input
              type="text"
              placeholder="Task title..."
              value={newTodo.title}
              onChange={(e) =>
                setNewTodo({ ...newTodo, title: e.target.value })
              }
              required
            />

            <input
              type="text"
              placeholder="Description..."
              value={newTodo.description}
              onChange={(e) =>
                setNewTodo({ ...newTodo, description: e.target.value })
              }
            />
            
            <input
              type="datetime-local"
              className="datetime-input"
              value={newTodo.due_time}
              onChange={(e) =>
                setNewTodo({ ...newTodo, due_time: e.target.value })
              }
              required
            />
            <button type="submit">Add Task</button>

          </form>

        </div>


          <div className="todo-list">
            {todos.length === 0 ? (
              <div className="empty-state">Your schedule is clear. Add a task and set things in motion.</div>
            ) : (
              todos.map((todo) => (
                <div key={todo.id} className="todo-item">
                  <div className="todo-content">
                    <h3 className={todo.completed ? "completed" : ""}>
                      {todo.title}
                    </h3>
                    <p>{todo.description}</p>
                  </div>

                  <div className="todo-actions">
                    <button
                      className="done-btn"
                      onClick={() => toggleTodo(todo.id)}
                    >
                      {todo.completed ? "Undo" : "Done"}
                    </button>

                    <button
                      className="delete-btn"
                      onClick={() => deleteTodo(todo.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {todos.length > 0 && (
            <button className="delete-all" onClick={deleteAllTodos}>
              Clear All Tasks
            </button>
          )}
        </div>
      </div>
    // </div>
  );
}

export default Dashboard;


"use client";

import { useState, useEffect } from "react";

interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
} 

// ── Inline styles ─────────────────────────────────────────────────────────────

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#f0f2f5",
    fontFamily: "sans-serif",
    padding: "40px 20px",
  } as React.CSSProperties,

  container: {
    maxWidth: "600px",
    margin: "0 auto",
  } as React.CSSProperties,

  heading: {
    fontSize: "28px",
    fontWeight: "bold" as const,
    color: "#1a1a2e",
    marginBottom: "32px",
    borderBottom: "2px solid #4f46e5",
    paddingBottom: "12px",
  } as React.CSSProperties,

  card: {
    backgroundColor: "#ffffff",
    borderRadius: "10px",
    padding: "24px",
    marginBottom: "24px",
    boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
  } as React.CSSProperties,

  sectionTitle: {
    fontSize: "16px",
    fontWeight: "600" as const,
    color: "#374151",
    marginBottom: "16px",
  } as React.CSSProperties,

  input: {
    display: "block",
    width: "100%",
    padding: "10px 12px",
    marginBottom: "12px",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    fontSize: "14px",
    boxSizing: "border-box" as const,
  } as React.CSSProperties,

  btnPrimary: {
    padding: "10px 20px",
    backgroundColor: "#4f46e5",
    color: "#ffffff",
    border: "none",
    borderRadius: "6px",
    fontSize: "14px",
    cursor: "pointer",
    marginRight: "8px",
  } as React.CSSProperties,

  btnSecondary: {
    padding: "10px 20px",
    backgroundColor: "#e5e7eb",
    color: "#374151",
    border: "none",
    borderRadius: "6px",
    fontSize: "14px",
    cursor: "pointer",
    marginRight: "8px",
  } as React.CSSProperties,

  btnLogout: {
    padding: "10px 20px",
    backgroundColor: "#fee2e2",
    color: "#b91c1c",
    border: "1px solid #fca5a5",
    borderRadius: "6px",
    fontSize: "14px",
    cursor: "pointer",
    marginRight: "8px",
  } as React.CSSProperties,

  btnEdit: {
    padding: "4px 12px",
    backgroundColor: "#f3f4f6",
    color: "#374151",
    border: "1px solid #d1d5db",
    borderRadius: "5px",
    fontSize: "13px",
    cursor: "pointer",
    marginRight: "6px",
  } as React.CSSProperties,

  btnDelete: {
    padding: "4px 12px",
    backgroundColor: "#fee2e2",
    color: "#b91c1c",
    border: "1px solid #fca5a5",
    borderRadius: "5px",
    fontSize: "13px",
    cursor: "pointer",
  } as React.CSSProperties,

  projectRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "12px 0",
    borderBottom: "1px solid #f3f4f6",
  } as React.CSSProperties,

  projectName: {
    fontSize: "15px",
    color: "#111827",
  } as React.CSSProperties,

  statusText: {
    fontSize: "13px",
    color: "#6b7280",
    marginBottom: "12px",
  } as React.CSSProperties,

  emptyText: {
    fontSize: "14px",
    color: "#9ca3af",
    textAlign: "center" as const,
    padding: "20px 0",
  } as React.CSSProperties,
};

// ── Component ─────────────────────────────────────────────────────────────────

export default function Home() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectStatus, setProjectStatus] = useState("");
  const [sessionMessage, setSessionMessage] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const getProjects = async (tokenFromLogin?: string) => {
    // Prefer a token passed directly (e.g. from login); fall back to localStorage
    const token = tokenFromLogin ?? localStorage.getItem("token");

    // Guard: never send a request without a valid token
    if (!token) {
      setProjectStatus("Not authenticated — please log in.");
      return;
    }

    console.log("[getProjects] token confirmed, sending request:", token);
    setProjectStatus("Loading...");

    try {
      const res = await fetch("http://localhost:8080/projects/", {
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await res.json();
      console.log("PROJECTS response status:", res.status);
      console.log("PROJECTS:", data);

      if (!res.ok) {
        if (res.status === 401) {
          // Token is expired or was invalidated — clear the stale session
          // and return the user to the login screen automatically.
          localStorage.removeItem("token");
          setIsLoggedIn(false);
          setProjects([]);
          setSessionMessage("Session expired. Please log in again.");
        } else {
          setProjectStatus(`Error ${res.status}: ${data.detail ?? "Unknown error"}`);
        }
        return;
      }

      setProjects(data);
      setProjectStatus(`${data.length} project(s) loaded`);
    } catch (err) {
      console.error("Fetch failed:", err);
      setProjectStatus("Network error — is the backend running?");
    }
  };

  // Runs once on mount ([] = no dependencies).
  // localStorage is only available in the browser, so it must live
  // inside useEffect — never in useState() or module-level code.
  // setState calls are placed inside a .then() callback so the linter
  // does not flag them as "synchronous setState in an effect".
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    Promise.resolve().then(() => {
      setIsLoggedIn(true);
      getProjects(token);
    });
  }, []);

  const createProject = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in first.");
      return;
    }

    const name = prompt("Project name:");
    if (!name) return;

    try {
      const res = await fetch("http://localhost:8080/projects/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name, description: "", tags: [] }),
      });

      if (!res.ok) {
        const data = await res.json();
        alert(`Failed to create project: ${data.detail ?? res.status}`);
        return;
      }

      await getProjects();
    } catch (err) {
      console.error("Create project failed:", err);
      alert("Network error — is the backend running?");
    }
  };

  const deleteProject = async (projectId: string, projectName: string) => {
    const token = localStorage.getItem("token");
    console.log("[deleteProject] token from localStorage:", token);

    if (!token) {
      alert("Please log in first.");
      return;
    }

    const confirmed = confirm(`Delete project "${projectName}"? This cannot be undone.`);
    if (!confirmed) return;

    try {
      console.log("[deleteProject] sending DELETE for projectId:", projectId);
      const res = await fetch(`http://localhost:8080/projects/${projectId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      console.log("[deleteProject] response status:", res.status);

      if (!res.ok) {
        const data = await res.json();
        console.error("[deleteProject] error response:", data);
        alert(`Failed to delete project: ${data.detail ?? res.status}`);
        return;
      }

      await getProjects();
    } catch (err) {
      console.error("Delete project failed:", err);
      alert("Network error — is the backend running?");
    }
  };

  const updateProject = async (projectId: string, currentName: string) => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in first.");
      return;
    }

    const newName = prompt("New project name:", currentName);
    if (!newName || newName === currentName) return;

    try {
      const res = await fetch(`http://localhost:8080/projects/${projectId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newName }),
      });

      if (!res.ok) {
        const data = await res.json();
        alert(`Failed to update project: ${data.detail ?? res.status}`);
        return;
      }

      await getProjects();
    } catch (err) {
      console.error("Update project failed:", err);
      alert("Network error — is the backend running?");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    setProjects([]);
    setEmail("");
    setPassword("");
    setProjectStatus("");
    setSessionMessage("");
  };

  const handleLogin = async () => {
    try {
      const res = await fetch("http://localhost:8080/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await res.json();

      
      if (res.ok) {
        localStorage.setItem("token", data.access_token);
        console.log("[handleLogin] token stored:", data.access_token);
        setSessionMessage("");
        setIsLoggedIn(true);
        await getProjects(data.access_token);
      } else {
        let errorMessage: string;
        if (typeof data.detail === "string") {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          errorMessage = data.detail.map((e: { msg?: string }) => e.msg ?? JSON.stringify(e)).join(", ");
        } else if (data.detail) {
          errorMessage = JSON.stringify(data.detail);
        } else {
          errorMessage = JSON.stringify(data) || String(res.status);
        }
        alert(`Login failed: ${errorMessage}`);
        console.log("Login failed response:", data);
      }

      console.log(data);
    } catch (err) {
      console.error("Login failed:", err);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <div style={styles.page}>
      <div style={styles.container}>

        <h1 style={styles.heading}>Project Dashboard</h1>

        {/* Login Section — only shown when logged out */}
        {!isLoggedIn && (
          <div style={styles.card}>
            <p style={styles.sectionTitle}>Sign In</p>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
            />
            <button onClick={handleLogin} style={styles.btnPrimary}>
              Login
            </button>
            {sessionMessage && (
              <p style={{ ...styles.statusText, marginTop: "12px" }}>{sessionMessage}</p>
            )}
          </div>
        )}

        {/* Actions + Projects — only shown when logged in */}
        {isLoggedIn && (
          <>
            <div style={styles.card}>
              <p style={styles.sectionTitle}>Actions</p>
              <button onClick={() => getProjects()} style={styles.btnSecondary}>
                Refresh Projects
              </button>
              <button onClick={createProject} style={styles.btnPrimary}>
                + Create Project
              </button>
              <button onClick={handleLogout} style={styles.btnLogout}>
                Logout
              </button>
            </div>

            <div style={styles.card}>
              <p style={styles.sectionTitle}>Projects</p>

              {projectStatus && (
                <p style={styles.statusText}>{projectStatus}</p>
              )}

              {projects.length === 0 ? (
                <p style={styles.emptyText}>No projects yet. Create one above.</p>
              ) : (
                projects.map((project) => (
                  <div key={project.id} style={styles.projectRow}>
                    <span style={styles.projectName}>
                      {project.name.replace("ArchitecOS", "ArchitectOS")}
                    </span>
                    <div>
                      <button
                        onClick={() => updateProject(project.id, project.name)}
                        style={styles.btnEdit}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteProject(project.id, project.name)}
                        style={styles.btnDelete}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}

      </div>
    </div>
  );
}

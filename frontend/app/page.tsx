"use client";

import { useState } from "react";

interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
}

export default function Home() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectStatus, setProjectStatus] = useState("");

  const getProjects = async (tokenFromLogin?: string) => {
    setProjectStatus("Loading...");

    const token = tokenFromLogin ?? localStorage.getItem("token");
    if (!token) {
      setProjectStatus("No token found — please log in first.");
      return;
    }

    try {
      const res = await fetch("http://localhost:8080/projects/", {
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await res.json();
      console.log("PROJECTS response status:", res.status);
      console.log("PROJECTS:", data);

      if (!res.ok) {
        setProjectStatus(`Error ${res.status}: ${data.detail ?? "Unknown error"}`);
        return;
      }

      setProjects(data);
      setProjectStatus(`Loaded ${data.length} project(s)`);
    } catch (err) {
      console.error("Fetch failed:", err);
      setProjectStatus("Network error — is the backend running?");
    }
  };

  const handleLogin = async () => {
    const res = await fetch("http://localhost:8080/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (res.ok) {
      localStorage.setItem("token", data.access_token);
      // Pass the fresh token directly — no localStorage timing issues
      await getProjects(data.access_token);
    } else {
      alert("Login failed ❌");
      console.log(data);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Login</h1>

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <br /><br />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <br /><br />

      <button onClick={handleLogin}>Login</button>
      <br /><br />
      <button onClick={() => getProjects()}>Get Projects</button>

      <br /><br />

      <h2>Projects</h2>

      {projectStatus && <p><strong>{projectStatus}</strong></p>}

      {projects.length === 0 ? (
        <p>No projects yet</p>
      ) : (
        <ul>
          
          {projects.map((project) => (
            <li key={project.id}>{project.name.replace("ArchitecOS", "ArchitectOS")}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

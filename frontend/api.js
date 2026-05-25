const API_BASE = "http://127.0.0.1:5001/api";

async function apiRequest(path, options = {}) {
  const authToken = localStorage.getItem("authToken");
  const requestOptions = {
    method: options.method || "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      ...(options.headers || {})
    }
  };

  if (options.body !== undefined) {
    requestOptions.body =
      typeof options.body === "string"
        ? options.body
        : JSON.stringify(options.body);
  }

  const response = await fetch(`${API_BASE}${path}`, requestOptions);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.message || `Request failed with ${response.status}`);
  }

  return data;
}

function getLoginState() {
  return {
    email: localStorage.getItem("loginEmail") || "",
    name: localStorage.getItem("loginName") || localStorage.getItem("userName") || "",
    role: localStorage.getItem("loginRole") || "",
    membership: localStorage.getItem("membership") || "0",
    authToken: localStorage.getItem("authToken") || ""
  };
}

function setLoginState(data, fallbackEmail, fallbackRole) {
  const displayName =
    data.display_name ||
    data.full_name ||
    data.company_name ||
    data.name ||
    localStorage.getItem("loginName") ||
    localStorage.getItem("userName") ||
    fallbackEmail ||
    "";

  localStorage.setItem("loginEmail", data.email || fallbackEmail || "");
  localStorage.setItem("loginName", displayName);
  localStorage.setItem("loginRole", data.role || fallbackRole || "");
  localStorage.setItem("membership", String(data.membership ?? "0"));

  if (data.auth_token) {
    localStorage.setItem("authToken", data.auth_token);
  }
}

function requireLogin(expectedRole) {
  const auth = getLoginState();

  if (!auth.email || !auth.role || !auth.authToken) {
    alert("Please log in first.");
    window.location.replace("SignIn.html");
    return null;
  }

  if (expectedRole && auth.role !== expectedRole) {
    alert("Please log in with the correct role.");
    window.location.replace("SignIn.html");
    return null;
  }

  return auth;
}

async function syncLoginState() {
  const auth = getLoginState();
  if (!auth.authToken) {
    return auth;
  }

  try {
    const data = await apiRequest("/me");
    if (data.loggedIn) {
      setLoginState(data, auth.email, auth.role);
      return getLoginState();
    }
  } catch (error) {
    console.warn("Unable to verify login state:", error.message);
  }

  clearLoginState();
  return getLoginState();
}

function clearLoginState() {
  localStorage.removeItem("loginEmail");
  localStorage.removeItem("loginName");
  localStorage.removeItem("loginRole");
  localStorage.removeItem("membership");
  localStorage.removeItem("authToken");
  localStorage.removeItem("candidateProfile");
  localStorage.removeItem("employerProfile");
  localStorage.removeItem("publishedJobs");
  localStorage.removeItem("userName");
}

async function logoutUser() {
  try {
    await apiRequest("/logout", {
      method: "POST"
    });
  } catch (error) {
    console.warn("Backend logout failed; clearing local session:", error.message);
  } finally {
    clearLoginState();
    window.location.replace("index.html");
  }
}

function drawUserMenu(element, auth, profileHref) {
  if (!auth.email || !auth.authToken) {
    element.textContent = "Guest";
    return;
  }

  element.innerHTML = "";

  const userBox = document.createElement("div");
  const nameNode = document.createElement(profileHref ? "a" : "strong");
  const strongNode = profileHref
    ? document.createElement("strong")
    : nameNode;

  strongNode.textContent = auth.name || auth.email;

  if (profileHref) {
    nameNode.href = profileHref;
    nameNode.appendChild(strongNode);
  }

  userBox.appendChild(nameNode);

  const logoutButton = document.createElement("button");
  logoutButton.type = "button";
  logoutButton.className = "logout-btn";
  logoutButton.textContent = "Logout";
  logoutButton.addEventListener("click", logoutUser);

  element.appendChild(userBox);
  element.appendChild(logoutButton);
}

function renderUserMenu(target, profileHref) {
  const element =
    typeof target === "string"
      ? document.getElementById(target)
      : target;

  if (!element) {
    return;
  }

  const auth = getLoginState();
  drawUserMenu(element, auth, profileHref);

  if (!auth.authToken) {
    return;
  }

  syncLoginState().then(freshAuth => {
    const freshProfileHref = freshAuth.role === "employer"
      ? "employer-profile.html"
      : freshAuth.role === "candidate"
        ? "candidate-profile.html"
        : profileHref;
    drawUserMenu(element, freshAuth, freshProfileHref);
  });
}

function skillsToArray(skills) {
  if (Array.isArray(skills)) {
    return skills;
  }
  if (!skills) {
    return [];
  }
  return String(skills)
    .split(",")
    .map(skill => skill.trim())
    .filter(Boolean);
}

function getLoggedInHomePage() {
  const auth = getLoginState();

  if (!auth.email || !auth.role || !auth.authToken) {
    return "index.html";
  }

  return auth.role === "employer"
    ? "employer-index.html"
    : "jobseeker-index.html";
}

function goHome(event) {
  if (event) {
    event.preventDefault();
  }

  window.location.href = getLoggedInHomePage();
}

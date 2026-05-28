import axios from "axios";

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Function to save the token in local storage
export function saveTokenToLocalStorage(token) {
  localStorage.setItem("authToken", token);
}

// Function to remove the token from local storage
function removeTokenFromLocalStorage() {
  localStorage.removeItem("authToken");
}

// Function to perform user login
// Function to perform user login
export const login = async (url, userData) => {
  try {
    const params = new URLSearchParams();
    params.append("grant_type", "password");
    params.append("username", userData.username);
    params.append("password", userData.password);
    params.append("scope", "");
    params.append("client_id", "");
    params.append("client_secret", "");

    const response = await instance.post(url, params, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    return response.data;
  } catch (error) {
    // Handle error, e.g., log it or throw a custom error
    console.error("Login error:", error);
    throw error;
  }
};

// Function to perform user logout
export function logout() {
  removeTokenFromLocalStorage();
}

// Function to refresh the authentication token (placeholder, replace with actual logic)
export async function refreshToken() {
  try {
    const response = await instance.post("/refresh-token-endpoint");
    const { token } = response.data;
    saveTokenToLocalStorage(token);
    return token;
  } catch (error) {
    // Handle error, e.g., log it or throw a custom error
    console.error("Refresh token error:", error);
    throw error;
  }
}

export default instance;

import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

// Helper to decode JWT payload safely
const parseJwt = (token: string) => {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch (e) {
    return null;
  }
};

const getInitialState = () => {
  const token = localStorage.getItem('token');
  if (token) {
    const payload = parseJwt(token);
    // Note: Since the backend doesn't return full user info in token,
    // this is a simplified user object derived from the token sub/role.
    if (payload) {
      return { 
        token, 
        user: { 
          id: payload.sub, 
          email: '', 
          full_name: '', 
          role: payload.role 
        } 
      };
    }
  }
  return { token: null, user: null };
};

export const useAuthStore = create<AuthState>((set) => ({
  ...getInitialState(),
  setAuth: (user, token) => {
    localStorage.setItem('token', token);
    set({ user, token });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null });
  },
}));

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type ThemeContextType = {
  dark: boolean;
  toggle: () => void;
  setDark: (v: boolean) => void;
};

const ThemeContext = createContext<ThemeContextType>({
  dark: false,
  toggle: () => {},
  setDark: () => {},
});

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [dark, setDarkState] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    const stored = localStorage.getItem("theme");
    if (stored) return stored === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <ThemeContext.Provider
      value={{ dark, toggle: () => setDarkState((d) => !d), setDark: setDarkState }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export const useTheme = () => useContext(ThemeContext);

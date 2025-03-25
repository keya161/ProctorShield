"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { type ThemeProviderProps } from "next-themes/dist/types";

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  const [docEnv, setDocEnv] = React.useState(false);

    React.useEffect(() => {
        if (typeof document !== "undefined") {
            setDocEnv(true);
        }
    }, []);
  
  return docEnv && <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}

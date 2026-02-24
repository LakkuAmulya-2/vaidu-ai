import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  language: string;
  setLanguage: (lang: string) => void;
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  recentQueries: Array<{ type: string; query: string; timestamp: number }>;
  addRecentQuery: (type: string, query: string) => void;
  clearRecentQueries: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      language: 'te',
      setLanguage: (lang) => set({ language: lang }),
      
      theme: 'light',
      toggleTheme: () => set((state) => ({ 
        theme: state.theme === 'light' ? 'dark' : 'light' 
      })),
      
      recentQueries: [],
      addRecentQuery: (type, query) => set((state) => ({
        recentQueries: [
          { type, query, timestamp: Date.now() },
          ...state.recentQueries.slice(0, 9)
        ]
      })),
      
      clearRecentQueries: () => set({ recentQueries: [] }),
    }),
    {
      name: 'vaidu-storage',
    }
  )
);
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { getMe, type MeResponse } from '../lib/auth';

type AuthState = {
  bearerToken: string;
  me: MeResponse | null;
  loading: boolean;
  setBearerToken: (token: string) => void;
  clearBearerToken: () => void;
  refresh: () => Promise<void>;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      bearerToken: '',
      me: null,
      loading: false,

      setBearerToken: (token) => {
        const trimmed = token.trim();
        set({ bearerToken: trimmed, me: null });
        if (trimmed) {
          void get().refresh();
        }
      },

      clearBearerToken: () => {
        set({ bearerToken: '', me: null });
      },

      refresh: async () => {
        const token = get().bearerToken;
        if (!token) return;
        set({ loading: true });
        try {
          const me = await getMe();
          set({ me, loading: false });
        } catch {
          set({ me: null, loading: false });
        }
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ bearerToken: state.bearerToken }),
    },
  ),
);

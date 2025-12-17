import { datastore } from './datastore.js';

export const auth = {
    // Register a new user
    signup: async (userProfile) => {
        // userProfile: { name, email, password, role }
        const user = await datastore.register(userProfile.name, userProfile.email, userProfile.password, userProfile.role);
        if (user) {
            return { success: true };
        } else {
            return { success: false, message: "Registration failed or Email taken" };
        }
    },

    // Login
    login: async (email, password) => {
        const user = await datastore.login(email, password);
        if (user) {
            return { success: true, user: user };
        } else {
            return { success: false, message: "Invalid credentials" };
        }
    },

    // Logout
    logout: () => {
        datastore.logout();
    },

    // Start Session (implicitly handled by login storing ID)
    startSession: () => {
        // No-op, managed by ID existence
    },

    // Check if logged in
    isAuthenticated: () => {
        return !!datastore.getCurrentUserId();
    },

    getUser: async () => {
        return await datastore.getMyProfile();
    },

    getUserId: () => {
        return datastore.getCurrentUserId();
    }
};

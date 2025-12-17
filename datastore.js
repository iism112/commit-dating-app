// API-based Datastore
const API_BASE = '/api';

function getHeaders() {
    const userId = localStorage.getItem('currentUserId');
    return {
        'Content-Type': 'application/json',
        'X-User-Id': userId || ''
    };
}
function getAuthHeaders() {
    const userId = localStorage.getItem('currentUserId');
    return {
        'X-User-Id': userId || ''
    };
}

export const datastore = {
    // Auth
    register: async (name, email, password, role) => {
        try {
            const res = await fetch(`${API_BASE}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password, role })
            });
            if (!res.ok) throw await res.json();
            const user = await res.json();
            localStorage.setItem('currentUserId', user.id);
            return user;
        } catch (e) {
            console.error("Register Error:", e);
            return null;
        }
    },

    login: async (email, password) => {
        try {
            const res = await fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            if (!res.ok) throw await res.json();
            const user = await res.json();
            localStorage.setItem('currentUserId', user.id);
            return user;
        } catch (e) {
            console.error("Login Error:", e);
            return null;
        }
    },

    logout: () => {
        localStorage.removeItem('currentUserId');
        window.location.href = 'login.html';
    },

    getCurrentUserId: () => {
        return localStorage.getItem('currentUserId');
    },

    // Save a like (or pass) action
    saveLike: async (profileId, type) => {
        try {
            const res = await fetch(`${API_BASE}/action`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({
                    target_id: profileId,
                    action_type: type
                })
            });
            return await res.json();
        } catch (e) {
            console.error("API Error saveLike:", e);
            return null;
        }
    },

    // Create Match (Legacy name from local logic, now effectively handled by backend check)
    // But frontend logic calls this to "save match". 
    // Actually backend `action` endpoint handles match creation.
    // So this might be redundant or we just use it to force valid state if needed.
    // Let's deprecate or make no-op, as backend does it.
    createMatch: async (profileId) => {
        // No-op, backend handles match on 'like'
    },

    // Get Matches
    getMatches: async () => {
        try {
            const res = await fetch(`${API_BASE}/matches`, { headers: getAuthHeaders() });
            return await res.json();
        } catch (e) {
            console.error("API Error getMatches:", e);
            return [];
        }
    },

    // Send Message
    sendMessage: async (matchPartnerId, text) => {
        try {
            await fetch(`${API_BASE}/messages`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({
                    match_id: matchPartnerId,
                    text: text
                })
            });
        } catch (e) {
            console.error("API Error sendMessage:", e);
        }
    },

    // Get Messages
    getMessages: async (matchPartnerId) => {
        try {
            const res = await fetch(`${API_BASE}/messages/${matchPartnerId}`, { headers: getAuthHeaders() });
            return await res.json();
        } catch (e) {
            console.error("API Error getMessages:", e);
            return [];
        }
    },

    // Get Profiles (Stack)
    getProfiles: async () => {
        try {
            const res = await fetch(`${API_BASE}/profiles`, { headers: getAuthHeaders() });
            return await res.json();
        } catch (e) {
            console.error("API Error getProfiles:", e);
            return [];
        }
    },

    // Get who liked me
    getWhoLikedMe: async () => {
        try {
            const res = await fetch(`${API_BASE}/likes/received`, { headers: getAuthHeaders() });
            return await res.json();
        } catch (e) {
            console.error("API Error getWhoLikedMe:", e);
            return [];
        }
    },

    // Get my likes
    getMyLikes: async () => {
        try {
            const res = await fetch(`${API_BASE}/likes/sent`, { headers: getAuthHeaders() });
            return await res.json();
        } catch (e) {
            console.error("API Error getMyLikes:", e);
            return [];
        }
    },

    // Get My Profile
    getMyProfile: async () => {
        try {
            const res = await fetch(`${API_BASE}/profile/me`, { headers: getAuthHeaders() });
            return await res.json();
        } catch (e) {
            console.error("API Error getMyProfile:", e);
            return null;
        }
    },

    // Update Profile
    updateProfile: async (data) => {
        try {
            const res = await fetch(`${API_BASE}/profile/me`, {
                method: 'PUT',
                headers: getHeaders(),
                body: JSON.stringify(data)
            });
            return await res.json();
        } catch (e) {
            console.error("API Error updateProfile:", e);
            return null;
        }
    },

    // Upload Image
    uploadImage: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        // Special case: FormData sets its own Content-Type boundary, so don't use getHeaders() with JSON type
        try {
            const res = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData
            });
            return await res.json();
        } catch (e) {
            console.error("API Error uploadImage:", e);
            return null;
        }
    },

    // Get Profile by ID
    getProfile: async (id) => {
        try {
            const res = await fetch(`${API_BASE}/profiles/${id}`, { headers: getAuthHeaders() });
            if (!res.ok) {
                console.error(`getProfile failed: ${res.status} ${res.statusText}`);
                return null;
            }
            return await res.json();
        } catch (e) {
            console.error("API Error getProfile:", e);
            return null;
        }
    },

    // Get Nearby
    getNearby: async (lat, lng) => {
        try {
            const res = await fetch(`${API_BASE}/nearby?lat=${lat}&lng=${lng}`, { headers: getAuthHeaders() });
            return await res.json();
        } catch (e) {
            console.error("API Error getNearby:", e);
            return [];
        }
    },

    // Get Unread Count
    getUnreadCount: async () => {
        try {
            const res = await fetch(`${API_BASE}/notifications`, { headers: getAuthHeaders() });
            if (!res.ok) return 0;
            const data = await res.json();
            return data.unread_count || 0;
        } catch (e) {
            console.error("API Error getUnreadCount:", e);
            return 0;
        }
    }
};

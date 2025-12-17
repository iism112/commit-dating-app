import mockProfiles from './mockData.js';
import { auth } from './auth.js';
import { datastore } from './datastore.js';

// State
let currentIndex = 0;
let profiles = [];
const stackContainer = document.getElementById('stack-container');
const endCard = document.getElementById('end-card');
const matchModal = document.getElementById('match-modal');
const matchName = document.getElementById('match-name');
const closeMatchBtn = document.getElementById('close-match');
let userLocation = null;

// Config
const THRESHOLD = 100; // px to trigger swipe

async function init() {
    getUserLocation();

    // Load User Profile for Header
    try {
        const myProfile = await datastore.getMyProfile();
        if (myProfile) {
            const avatarParams = document.getElementById('user-avatar');
            const nameDisplay = document.getElementById('user-display');
            if (avatarParams) avatarParams.src = myProfile.image || `https://ui-avatars.com/api/?name=${myProfile.name}`;
            if (nameDisplay) nameDisplay.textContent = myProfile.name;
        }
    } catch (e) {
        console.error("Failed to load my profile", e);
    }

    // Fetch profiles from API
    try {
        const rawProfiles = await datastore.getProfiles();
        // Normalize API data (flat location) to App data (nested location)
        profiles = rawProfiles.map(p => ({
            ...p,
            location: { lat: p.location_lat, lng: p.location_lng }
        }));
    } catch (e) {
        console.error("Failed to load profiles", e);
    }

    renderStack();
    setupControls();
}

function getUserLocation() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition((position) => {
            userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            console.log("User Location:", userLocation);
            // Re-render to show distances if they weren't there
            renderStack();
        }, (error) => {
            console.log("Location access denied or error:", error);
            // Fallback for demo if denied: NYC
            userLocation = { lat: 40.7128, lng: -74.0060 };
            renderStack();
        });
    } else {
        console.log("Geolocation not supported");
        userLocation = { lat: 40.7128, lng: -74.0060 }; // Fallback
        renderStack();
    }
}

function getDistance(loc1, loc2) {
    if (!loc1 || !loc2) return null;
    const R = 6371; // Radius of the earth in km
    const dLat = deg2rad(loc2.lat - loc1.lat);
    const dLon = deg2rad(loc2.lng - loc1.lng);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(deg2rad(loc1.lat)) * Math.cos(deg2rad(loc2.lat)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const d = R * c; // Distance in km
    return Math.round(d);
}

function deg2rad(deg) {
    return deg * (Math.PI / 180);
}

function renderStack() {
    const existingCards = document.querySelectorAll('.profile-card');
    existingCards.forEach(c => c.remove());

    if (currentIndex >= profiles.length) {
        endCard.classList.remove('hidden');
        return;
    }

    // Render Next Card (Background)
    if (currentIndex + 1 < profiles.length) {
        const nextCard = createCard(profiles[currentIndex + 1]);
        nextCard.style.transform = 'scale(0.95) translateY(10px)';
        nextCard.style.zIndex = 9;
        stackContainer.appendChild(nextCard);
    }

    // Render Current Card (Foreground)
    const currentCard = createCard(profiles[currentIndex]);
    currentCard.style.zIndex = 10;
    initSwipe(currentCard);
    stackContainer.appendChild(currentCard);

    // Re-init icons for new content
    if (window.lucide) window.lucide.createIcons();
}

function createCard(profile) {
    const card = document.createElement('div');
    card.className = 'profile-card overflow-hidden bg-github-card border border-github-border rounded-2xl flex flex-col';

    // Tech Stack Badges
    const stackHtml = profile.stack.map(tech =>
        `<span class="px-2 py-1 text-xs font-mono rounded-full border border-github-border text-github-text bg-github-bg/50">${tech}</span>`
    ).join('');

    // Distance Calculation
    let distanceHtml = '';
    if (userLocation && profile.location) {
        // Dynamic mock location logic for demo:
        // Assume profile is at (UserLoc + Offset) so they are always "local"
        const realProfileLoc = {
            lat: userLocation.lat + profile.location.lat,
            lng: userLocation.lng + profile.location.lng
        };
        const dist = getDistance(userLocation, realProfileLoc);
        distanceHtml = `
            <div class="flex items-center gap-1 text-github-muted text-xs font-mono mt-1">
                <i data-lucide="map-pin" class="w-3 h-3"></i>
                <span>${dist} km away</span>
            </div>
        `;
    }

    // Match Score Badge Color
    let scoreColor = 'bg-github-muted';
    if (profile.match_score >= 80) scoreColor = 'bg-github-green';
    else if (profile.match_score >= 50) scoreColor = 'bg-yellow-600';

    card.innerHTML = `
        <div class="stamp stamp-like transform -rotate-12 border-4 border-github-green text-github-green rounded px-2 font-bold text-2xl absolute top-8 left-8 z-20 opacity-0 pointer-events-none">MERGE</div>
        <div class="stamp stamp-nope transform rotate-12 border-4 border-github-red text-github-red rounded px-2 font-bold text-2xl absolute top-8 right-8 z-20 opacity-0 pointer-events-none">CLOSE</div>
        
        <div class="h-3/5 w-full relative">
            <img src="${profile.image}" class="w-full h-full object-cover pointer-events-none" alt="${profile.name}">
            <div class="absolute inset-0 bg-gradient-to-t from-github-card to-transparent"></div>
            
            <!-- Match Badge -->
            <div class="absolute top-4 right-4 ${scoreColor} text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg border border-white/20">
                ${profile.match_score}% Match
            </div>

            <!-- Info Button -->
             <button class="absolute top-4 left-4 bg-black/40 hover:bg-black/60 text-white p-2 rounded-full backdrop-blur transition border border-white/10 z-20"
                onmousedown="event.stopPropagation();" 
                onclick="event.stopPropagation(); window.location.href='view-profile.html?id=${profile.id}&return=index'">
                <i data-lucide="info" class="w-5 h-5"></i>
            </button>

            <div class="absolute bottom-4 left-4">
                <h2 class="text-2xl font-bold text-white shadow-black drop-shadow-md">${profile.name}</h2>
                <div class="flex flex-col">
                    <p class="text-github-accent font-mono text-sm">${profile.role}</p>
                    ${distanceHtml}
                </div>
            </div>
        </div>
        <div class="flex-1 p-4 bg-github-card flex flex-col gap-3">
             <div class="flex flex-wrap gap-2">
                ${stackHtml}
             </div>
             <p class="text-github-text text-sm font-mono leading-relaxed opacity-90 mt-2">
                > ${profile.bio}
             </p>
        </div>
    `;

    return card;
}

function initSwipe(card) {
    let startX = 0;
    let currentX = 0;
    let isDragging = false;
    let startTime = 0;
    let velocity = 0;

    const likeStamp = card.querySelector('.stamp-like');
    const nopeStamp = card.querySelector('.stamp-nope');

    const start = (x) => {
        isDragging = true;
        startX = x;
        startTime = Date.now();
        card.style.transition = 'none';
    };

    const move = (x) => {
        if (!isDragging) return;

        // Calculate raw delta
        const deltaX = x - startX;
        currentX = deltaX;

        // Rotation physics: clamp rotation to avoid spinning too much
        const rotate = Math.max(Math.min(currentX * 0.1, 15), -15);

        card.style.transform = `translateX(${currentX}px) rotate(${rotate}deg)`;

        // Opacity math for stamps
        const opacity = Math.min(Math.abs(currentX) / (THRESHOLD * 0.5), 1);

        if (currentX > 0) {
            likeStamp.style.opacity = opacity;
            nopeStamp.style.opacity = 0;
        } else {
            nopeStamp.style.opacity = opacity;
            likeStamp.style.opacity = 0;
        }
    };

    const end = (x) => {
        if (!isDragging) return;
        isDragging = false;

        // Calculate velocity (pixels per ms)
        const dt = Date.now() - startTime;
        if (dt > 0) velocity = (x - startX) / dt;

        // Thresholds
        const isSwipe = Math.abs(currentX) > THRESHOLD || Math.abs(velocity) > 0.5; // Velocity throw support

        if (isSwipe) {
            // Success Swipe
            // If threw with velocity, use that direction. Else use position.
            const direction = (currentX > 0 || velocity > 0.5) ? 'right' : 'left';
            if (direction === 'right' && currentX < 0) { /* Correction if mixed signals, assume pos */ }
            // Actually simple logic: if huge pos, take pos. If small pos but huge velocity, take velocity.

            const finalDir = currentX > 0 ? 'right' : 'left'; // Simple fallback

            card.style.transition = 'transform 0.3s ease-out';
            dismissCard(card, finalDir);
        } else {
            // Snap back
            card.style.transition = 'transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1)'; // Bouncy Ease
            resetCard(card);
        }
    };

    card.addEventListener('touchstart', (e) => start(e.touches[0].clientX));
    card.addEventListener('touchmove', (e) => move(e.touches[0].clientX));
    card.addEventListener('touchend', (e) => end(e.changedTouches[0].clientX));

    card.addEventListener('mousedown', (e) => start(e.clientX));
    document.addEventListener('mousemove', (e) => { if (isDragging) move(e.clientX); });
    document.addEventListener('mouseup', (e) => { if (isDragging) end(e.clientX); });

    function resetCard(card) {
        card.style.transform = 'translateX(0) rotate(0)';
        likeStamp.style.opacity = 0;
        nopeStamp.style.opacity = 0;
    }
}

function dismissCard(card, direction) {
    const screenWidth = window.innerWidth;
    const moveX = direction === 'right' ? screenWidth : -screenWidth;
    const rotate = direction === 'right' ? 30 : -30;
    card.style.transform = `translateX(${moveX}px) rotate(${rotate}deg)`;

    const profile = profiles[currentIndex];
    setTimeout(() => {
        card.remove();
        currentIndex++;
        renderStack();

        // Save Action & Check Match via API
        datastore.saveLike(profile.id, direction === 'right' ? 'like' : 'pass')
            .then(res => {
                if (direction === 'right' && res && res.match) {
                    matchName.textContent = profile.name.split(' ')[0];
                    matchModal.classList.add('active');

                    // Setup "Start Chat" button
                    const startChatBtn = document.getElementById('btn-start-chat');
                    if (startChatBtn) {
                        startChatBtn.onclick = (e) => {
                            // ensure it's a number and valid
                            if (profile && typeof profile.id === 'number' && profile.id > 0) {
                                window.location.href = `chat.html?id=${profile.id}`;
                            } else {
                                console.error("Cannot start chat: Invalid Profile ID", profile);
                                alert("Error: Could not start chat. Please refresh.");
                            }
                        };
                    }
                }
            });
    }, 300);
}





function setupControls() {
    document.getElementById('btn-like').addEventListener('click', () => {
        const currentCard = document.querySelector('.profile-card:last-child');
        if (currentCard && currentIndex < profiles.length) {
            currentCard.style.transition = 'transform 0.5s ease-out';
            dismissCard(currentCard, 'right');
        }
    });

    document.getElementById('btn-pass').addEventListener('click', () => {
        const currentCard = document.querySelector('.profile-card:last-child');
        if (currentCard && currentIndex < profiles.length) {
            currentCard.style.transition = 'transform 0.5s ease-out';
            dismissCard(currentCard, 'left');
        }
    });

    document.getElementById('btn-refresh').addEventListener('click', () => {
        currentIndex = 0;
        renderStack();
        endCard.classList.add('hidden');
    });

    closeMatchBtn.addEventListener('click', () => {
        matchModal.classList.remove('active');
    });
}

// Notification Polling
async function checkNotifications() {
    try {
        const unread = await datastore.getUnreadCount();
        console.log("Debug: Unread Count =", unread);

        // Find the Matches icon link (in nav)
        // We look for the link ending in matches.html
        const matchesLink = document.querySelector('a[href="matches.html"]');
        console.log("Debug: Matches Link Found =", !!matchesLink);

        if (matchesLink) {
            let badge = matchesLink.querySelector('.notification-badge');

            if (unread > 0) {
                if (!badge) {
                    badge = document.createElement('div');
                    badge.className = 'notification-badge absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center border border-github-bg';
                    matchesLink.style.position = 'relative';
                    matchesLink.appendChild(badge);
                }
                badge.textContent = unread > 9 ? '9+' : unread;
            } else {
                if (badge) badge.remove();
            }
        }
    } catch (e) {
        console.error("Debug: Notification Check Failed", e);
    }
}

// Start App
init();

// Poll for notifications every 5 seconds
setInterval(checkNotifications, 5000);
// Check immediately
checkNotifications();

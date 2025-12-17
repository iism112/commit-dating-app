const mockProfiles = [
    {
        id: 1,
        name: "Sarah Chen",
        role: "Frontend Architect",
        bio: "git commit -m 'looking for someone to center my div'",
        stack: ["React", "TypeScript", "Tailwind", "Three.js"],
        image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=500&q=80",
        location: { lat: 0.01, lng: 0.01 } // Relative offsets for demo
    },
    {
        id: 2,
        name: "Alex Rodriguez",
        role: "Systems Engineer",
        bio: "Rust enthusiast. I promise not to rewrite your codebase.",
        stack: ["Rust", "Go", "Kubernetes", "Linux"],
        image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=500&q=80",
        location: { lat: -0.02, lng: 0.005 }
    },
    {
        id: 3,
        name: "Jordan Taylor",
        role: "AI Researcher",
        bio: "Training models by day, debugging life by night.",
        stack: ["Python", "PyTorch", "TensorFlow", "CUDA"],
        image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=500&q=80",
        location: { lat: 0.015, lng: -0.01 }
    },
    {
        id: 4,
        name: "Emily Zhang",
        role: "Full Stack Dev",
        bio: "Tabs over spaces. VIM over VS Code. Fight me.",
        stack: ["Node.js", "Vue", "Postgres", "AWS"],
        image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=500&q=80",
        location: { lat: -0.005, lng: -0.02 }
    },
    {
        id: 5,
        name: "David Kim",
        role: "DevOps Engineer",
        bio: "If it works on my machine, we ship my machine.",
        stack: ["Docker", "Terraform", "CI/CD", "Bash"],
        image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=500&q=80",
        location: { lat: 0.03, lng: 0.03 }
    }
];

export default mockProfiles;

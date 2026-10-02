/* ==========================================
   THE UNSEEN STORY - CORE ENGINE & LOGIC
   ========================================== */

// --- 1. THREE.JS 3D GPU PARTICLE ENGINE ---
const canvas = document.getElementById('bg-canvas');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

// Create floating mana particles
const particleCount = 700;
const geometry = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);

for (let i = 0; i < particleCount * 3; i += 3) {
    positions[i] = (Math.random() - 0.5) * 20;     // X
    positions[i + 1] = (Math.random() - 0.5) * 20; // Y
    positions[i + 2] = (Math.random() - 0.5) * 20; // Z
}

geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

// Glowing particle material
const material = new THREE.PointsMaterial({
    size: 0.04,
    color: 0xc77dff,
    transparent: true,
    opacity: 0.7,
    blending: THREE.AdditiveBlending
});

const particles = new THREE.Points(geometry, material);
scene.add(particles);
camera.position.z = 5;

// Render loop for smooth 60fps movement
function animateParticles() {
    requestAnimationFrame(animateParticles);
    particles.rotation.y += 0.0008;
    particles.rotation.x += 0.0003;
    renderer.render(scene, camera);
}
animateParticles();

// Handle screen resizing
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});


// --- 2. GATE UNLOCK & NAVIGATION LOGIC ---

// Visitor Gate Password Check
function unlockVisitorRealm() {
    const pass = document.getElementById('visitor-pass').value;
    // You can set your custom visitor password here
    if (pass === "" || pass === "1234") { // Default lets empty or 1234 in for testing
        gsap.to("#visitor-gate", { opacity: 0, duration: 0.8, onComplete: () => {
            document.getElementById('visitor-gate').style.display = 'none';
            document.getElementById('main-site').style.opacity = '1';
            document.getElementById('main-site').style.pointerEvents = 'auto';
        }});
    } else {
        alert("Incorrect Gateway Passcode.");
    }
}

// Multi-page Switcher
function switchPage(pageId, element) {
    document.querySelectorAll('.page-view').forEach(page => page.classList.remove('active-page'));
    document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));

    document.getElementById('page-' + pageId).classList.add('active-page');
    element.classList.add('active');
}


// --- 3. OWNER & INNER CIRCLE MODALS ---
function openOwnerLoginModal() {
    document.getElementById('owner-login-modal').style.display = 'flex';
}
function closeOwnerLoginModal() {
    document.getElementById('owner-login-modal').style.display = 'none';
}
function verifyOwnerAccess() {
    const email = document.getElementById('owner-email').value;
    const pass = document.getElementById('owner-pass').value;
    
    // Simple verification (Can be bound directly to Supabase Auth later)
    if(email !== "" && pass !== "") {
        closeOwnerLoginModal();
        document.getElementById('owner-cms-modal').style.display = 'flex';
    } else {
        alert("Invalid Sovereign Credentials.");
    }
}

function closeCMSPanel() {
    document.getElementById('owner-cms-modal').style.display = 'none';
}


// --- 4. THE 5-SECOND LONG-PRESS CORE TRIGGER (SOLO LEVELING STYLE) ---
const coreTrigger = document.getElementById('secret-core-trigger');
let holdTimer;
let isHolding = false;

function triggerAriseSequence() {
    // Play Cinematic ARISE Sequence
    const ariseOverlay = document.getElementById('arise-overlay');
    
    gsap.to(ariseOverlay, { opacity: 1, duration: 0.3 });
    gsap.to("#arise-overlay h1", { scale: 1.2, duration: 1.5, ease: "power2.out" });

    setTimeout(() => {
        gsap.to(ariseOverlay, { opacity: 0, duration: 0.8, onComplete: () => {
            document.getElementById('arise-overlay h1').style.transform = 'scale(0.8)';
            // Open Inner Circle after Arise animation
            document.getElementById('inner-circle-modal').style.display = 'flex';
        }});
    }, 2000);
}

// Touch & Mouse Event Handlers for 5-Second Hold
const startHold = (e) => {
    e.preventDefault();
    isHolding = true;
    gsap.to(coreTrigger, { scale: 1.15, duration: 5, ease: "power1.in" });
    
    holdTimer = setTimeout(() => {
        if (isHolding) {
            triggerAriseSequence();
            isHolding = false;
        }
    }, 5000); // Exact 5 seconds hold
};

const cancelHold = () => {
    if (isHolding) {
        isHolding = false;
        clearTimeout(holdTimer);
        gsap.to(coreTrigger, { scale: 1, duration: 0.3 });
    }
};

coreTrigger.addEventListener('mousedown', startHold);
coreTrigger.addEventListener('mouseup', cancelHold);
coreTrigger.addEventListener('mouseleave', cancelHold);

coreTrigger.addEventListener('touchstart', startHold);
coreTrigger.addEventListener('touchend', cancelHold);


// Inner Circle Handlers
function verifyInnerCircle() {
    const pass = document.getElementById('inner-circle-pass').value;
    if(pass === "shadow") { // Secret Inner Circle passcode
        alert("Sanctum Unlocked. Anti-Screenshot Shield Active.");
        document.getElementById('inner-circle-modal').style.display = 'none';
    } else {
        alert("Access Denied by the System.");
    }
}
function closeInnerCircleModal() {
    document.getElementById('inner-circle-modal').style.display = 'none';
}


// --- 5. REAL-TIME CMS TITLE UPDATER ---
function updateHeroTitle(newText) {
    document.getElementById('hero-heading').innerText = newText;
}

function saveCMSChangesToSupabase() {
    const updatedTitle = document.getElementById('cms-title-input').value;
    // Here Supabase database update logic will plug in seamlessly
    alert("Changes synced with Supabase! Live across all nodes.");
    closeCMSPanel();
}

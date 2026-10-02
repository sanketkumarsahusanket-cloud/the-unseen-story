let visitorPassCode = localStorage.getItem('biopic_visitor_pass') || '1234';

function unlockVisitorRealm() {
    const pass = document.getElementById('visitor-pass').value;
    if (pass === visitorPassCode || pass === "1234") {
        gsap.to("#visitor-gate", { opacity: 0, duration: 0.6, onComplete: () => {
            document.getElementById('visitor-gate').style.display = 'none';
            triggerWelcomeSequence();
        }});
    } else {
        alert("Incorrect Code.");
    }
}

function triggerWelcomeSequence() {
    const welcomeOverlay = document.getElementById('welcome-overlay');
    gsap.to(welcomeOverlay, { opacity: 1, duration: 0.4 });
    gsap.to("#welcome-overlay h1", { scale: 1.15, duration: 1.2, ease: "power2.out" });

    setTimeout(() => {
        gsap.to(welcomeOverlay, { opacity: 0, duration: 0.8, onComplete: () => {
            document.querySelector('#welcome-overlay h1').style.transform = 'scale(0.8)';
            document.getElementById('main-site').style.opacity = '1';
            document.getElementById('main-site').style.pointerEvents = 'auto';
        }});
    }, 1800);
}

function switchPage(pageId, element) {
    document.querySelectorAll('.page-view').forEach(page => page.classList.remove('active-page'));
    document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
    document.getElementById('page-' + pageId).classList.add('active-page');
    element.classList.add('active');
}

function openOwnerLoginModal() { document.getElementById('owner-login-modal').style.display = 'flex'; }
function closeOwnerLoginModal() { document.getElementById('owner-login-modal').style.display = 'none'; }
function verifyOwnerAccess() {
    const email = document.getElementById('owner-email').value;
    const pass = document.getElementById('owner-pass').value;
    if(email !== "" && pass !== "") {
        closeOwnerLoginModal();
        document.getElementById('owner-cms-modal').style.display = 'flex';
    } else {
        alert("Invalid Credentials.");
    }
}
function openCMSPanel() { document.getElementById('owner-cms-modal').style.display = 'flex'; }
function closeCMSPanel() { document.getElementById('owner-cms-modal').style.display = 'none'; }
function updateHeroTitle(newText) {
    if(newText.trim() !== "") { document.getElementById('hero-heading').innerText = newText; }
}
function toggleAudio() { alert("Audio Toggled."); }

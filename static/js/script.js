document.addEventListener("click", function (event) {
  const navLinks = document.getElementById("navLinks");
  const menuToggle = document.querySelector(".menu-toggle");

  // Agar menu open hai, aur click menu ke bahar hua ho
  if (navLinks && menuToggle &&
      navLinks.classList.contains("active") &&
      !navLinks.contains(event.target) &&
      !menuToggle.contains(event.target)) {
    navLinks.classList.remove("active");
  }
});

// Apply persisted dark mode only if user has previously chosen.
// Do not auto-toggle based on system or other criteria.
document.addEventListener("DOMContentLoaded", () => {
  const darkPref = localStorage.getItem("darkMode"); // "enabled" | "disabled" | null
  if (darkPref === "enabled") {
    document.body.classList.add("dark-mode");
  } else if (darkPref === "disabled") {
    document.body.classList.remove("dark-mode");
  }
});

function toggleMode() {
  const nowDark = document.body.classList.toggle("dark-mode");
  // Persist the user's explicit choice so reload keeps it.
  localStorage.setItem("darkMode", nowDark ? "enabled" : "disabled");
}

function toggleMenu() {
  document.getElementById("navLinks").classList.toggle("active");
}

function openModal(type) {
  document.getElementById("blurBg").classList.add("active");
  document.body.style.overflow = "hidden";
  if (type === 'login') {
    document.getElementById("loginModal").classList.add("active");
  } else {
    document.getElementById("registerModal").classList.add("active");
  }
}

function closeModal() {
  document.getElementById("blurBg").classList.remove("active");
  document.getElementById("loginModal").classList.remove("active");
  document.getElementById("registerModal").classList.remove("active");
  document.body.style.overflow = "auto";
}

function switchModal(type) {
  closeModal();
  setTimeout(() => openModal(type), 300);
}

// Notice close button
// Shared notice-bar injection for all pages that load this script.
(function(){
  var NOTICE_ID = 'noticeBar';
  var DURATION = 30000; // 30 seconds

  function createNotice(){
    if(document.getElementById(NOTICE_ID)) return; // don't duplicate if page already has it

    var container = document.createElement('div');
    container.id = NOTICE_ID;
    container.className = 'notice-bar';
    container.innerHTML = '<div class="notice-content">📢 Free live doubt-clearing this Saturday • Admissions open for 2025</div>' +
                          '<button class="notice-close" aria-label="Close notice">&times;</button>';

    document.body.insertBefore(container, document.body.firstChild);

    if(!document.getElementById('notice-bar-styles')){
      var s = document.createElement('style'); s.id = 'notice-bar-styles';
      s.textContent =
        '.notice-bar{background:#007bff;color:#fff;padding:10px 16px;display:flex;justify-content:space-between;align-items:center;gap:10px;transform:translateY(-120%);position:relative;z-index:9999}\\n' +
        '.notice-bar.show{transform:translateY(0);transition:transform .5s cubic-bezier(.2,.9,.2,1)}\\n' +
        '.notice-bar .notice-content{font-weight:600}\\n' +
        '.notice-close{background:transparent;border:0;color:#fff;font-size:20px;cursor:pointer}\\n';
      document.head.appendChild(s);
    }

    container.querySelector('.notice-close').addEventListener('click', function(){ hideNotice(container); });
  }

  function showNotice(el){
    if(!el) el = document.getElementById(NOTICE_ID);
    if(!el) return;
    el.style.display = 'flex';
    void el.offsetWidth;
    el.classList.add('show');
  }

  function hideNotice(el){
    if(!el) el = document.getElementById(NOTICE_ID);
    if(!el) return;
    el.classList.remove('show');
    setTimeout(function(){ if(el && el.parentNode) el.parentNode.removeChild(el); }, 600);
  }

  document.addEventListener('DOMContentLoaded', function(){
    createNotice();
    var nb = document.getElementById(NOTICE_ID);
    if(!nb) return;
    setTimeout(function(){ showNotice(nb); }, 220);
    setTimeout(function(){ hideNotice(nb); }, DURATION + 300);
  });
})();
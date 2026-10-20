/* ============================================
   MODAL SYSTEM
   ============================================ */

const overlay   = document.getElementById('modalOverlay');
const modal     = overlay.querySelector('.modal');
const titleEl   = document.getElementById('modalTitle');
const form      = document.getElementById('modalForm');
const closeBtn  = document.getElementById('modalClose');
const cancelBtn = document.getElementById('modalCancel');
const allBodies = overlay.querySelectorAll('.modal-body');

/* ---- Config: what form to show per action ---- */
const MODAL_CONFIG = {
  student: { title: 'Add Student' },
  course:  { title: 'Add Course'  },
  grade:   { title: 'Add Grade'   },
};

/* ---- Open modal ---- */
function openModal(type = 'student') {
  // Show only the matching form body
  allBodies.forEach(body => {
    body.hidden = body.dataset.form !== type;
  });

  // Set title
  titleEl.textContent = MODAL_CONFIG[type]?.title || 'Form';

  // Show overlay
  overlay.classList.add('active');
  overlay.setAttribute('aria-hidden', 'false');

  // Focus first input after transition
  setTimeout(() => {
    const firstInput = overlay.querySelector(`[data-form="${type}"] input, [data-form="${type}"] select`);
    firstInput?.focus();
  }, 100);

  // Prevent background scroll
  document.body.style.overflow = 'hidden';
}

/* ---- Close modal ---- */
function closeModal() {
  overlay.classList.remove('active');
  overlay.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
  form.reset();

  // Hide all bodies again
  allBodies.forEach(body => (body.hidden = body.dataset.form !== 'student'));
}

/* ---- Triggers: any button with data-modal opens a form ---- */
document.querySelectorAll('[data-modal]').forEach(btn => {
  btn.addEventListener('click', () => {
    openModal(btn.dataset.modal);
  });
});

/* ---- Close handlers ---- */
closeBtn.addEventListener('click', closeModal);
cancelBtn.addEventListener('click', closeModal);

// Click outside the modal box closes it
overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closeModal();
});

// Escape key closes it
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && overlay.classList.contains('active')) {
    closeModal();
  }
});

/* ---- Form submit ---- */
form.addEventListener('submit', (e) => {
  e.preventDefault();

  // Determine which form is currently visible
  const visibleBody = [...allBodies].find(b => !b.hidden);
  const formType = visibleBody?.dataset.form;

  // Collect form data
  const data = Object.fromEntries(new FormData(form).entries());

  console.log(`Submitting ${formType}:`, data);

  // TODO: Send to backend (fetch/axios)
  // await fetch('/api/students', { method: 'POST', body: JSON.stringify(data) });

  closeModal();
});

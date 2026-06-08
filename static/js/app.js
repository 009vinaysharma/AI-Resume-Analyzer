/* AI Resume Analyzer – Frontend JavaScript */

const dropZone    = document.getElementById('dropZone');
const fileInput   = document.getElementById('fileInput');
const fileSelected= document.getElementById('fileSelected');
const analyzeForm = document.getElementById('analyzeForm');
const progressWrap= document.getElementById('progressWrap');
const progressBar = document.getElementById('progressBar');
const submitBtn   = document.getElementById('submitBtn');

if (dropZone) {
  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragging'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragging'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault(); dropZone.classList.remove('dragging');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });
  fileInput.addEventListener('change', () => { if (fileInput.files[0]) handleFile(fileInput.files[0]); });
}

function handleFile(file) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    showToast('Please upload a PDF file.', 'error'); return;
  }
  const dt = new DataTransfer(); dt.items.add(file); fileInput.files = dt.files;
  fileSelected.textContent = '✓ ' + file.name + ' (' + (file.size/1024).toFixed(1) + ' KB)';
}

if (analyzeForm) {
  analyzeForm.addEventListener('submit', function(e) {
    if (!fileInput.files || !fileInput.files[0]) {
      e.preventDefault(); showToast('Please select a PDF resume first.', 'error'); return;
    }
    submitBtn.disabled = true; submitBtn.textContent = 'Analyzing…';
    if (progressWrap) progressWrap.style.display = 'block';
    var pct = 0;
    var iv = setInterval(function() {
      pct = Math.min(pct + Math.random()*12, 90);
      if (progressBar) progressBar.style.width = pct + '%';
    }, 400);
    window.addEventListener('beforeunload', function() { clearInterval(iv); });
  });
}

document.querySelectorAll('.flash').forEach(function(el) {
  setTimeout(function() {
    el.style.transition = 'opacity .5s'; el.style.opacity = '0';
    setTimeout(function() { el.remove(); }, 500);
  }, 4000);
});

function showToast(msg, type) {
  var toast = document.createElement('div');
  toast.className = 'flash flash-' + (type === 'error' ? 'error' : 'success');
  toast.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;min-width:260px;';
  toast.textContent = msg; document.body.appendChild(toast);
  setTimeout(function() { toast.style.transition = 'opacity .5s'; toast.style.opacity = '0'; }, 3000);
  setTimeout(function() { toast.remove(); }, 3600);
}

var ring = document.getElementById('ringFill');
if (ring) {
  setTimeout(function() {
    var m = ring.getAttribute('style').match(/--score:\s*([\d.]+)/);
    var score = m ? parseFloat(m[1]) : 0;
    ring.style.strokeDashoffset = String(314 - (314 * score / 100));
  }, 300);
}

var observer = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      entry.target.style.animation = 'fadeUp .6s ease both';
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });
document.querySelectorAll('.feature-card, .result-card, .result-panel').forEach(function(el) {
  observer.observe(el);
});

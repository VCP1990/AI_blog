document.addEventListener('DOMContentLoaded', function() {
  const sections = document.querySelectorAll('.animate-section');
  
  const observerOptions = {
    root: null,
    rootMargin: '0px 0px -100px 0px',
    threshold: 0.1
  };
  
  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  sections.forEach(function(section) {
    observer.observe(section);
  });
  
  const firstSection = document.querySelector('.animate-section');
  if (firstSection) {
    setTimeout(function() {
      firstSection.classList.add('visible');
    }, 100);
  }
});

document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    var targetId = this.getAttribute('href');
    if (targetId && targetId !== '#') {
      var target = document.querySelector(targetId);
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    }
  });
});

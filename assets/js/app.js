/**
 * Alexandria Sanctuary - Main Application
 * Contemplative, slow interactions
 */

(function() {
  'use strict';

  // ============================================
  // INTRO OVERLAY
  // ============================================
  const IntroOverlay = {
    init() {
      const overlay = document.getElementById('introOverlay');
      if (!overlay) return;

      // Hide after quote is read
      setTimeout(() => {
        overlay.classList.add('is-hidden');
      }, 4500);

      // Skip on click
      overlay.addEventListener('click', () => {
        overlay.classList.add('is-hidden');
      });
    }
  };

  // ============================================
  // NAVIGATION
  // ============================================
  const Navigation = {
    init() {
      const nav = document.getElementById('nav');

      // Scroll behavior
      window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
          nav?.classList.add('is-scrolled');
        } else {
          nav?.classList.remove('is-scrolled');
        }
      }, { passive: true });

      // Smooth scroll for anchor links
      document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
          const href = link.getAttribute('href');
          if (href === '#') return;

          const target = document.querySelector(href);
          if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        });
      });
    }
  };

  // ============================================
  // SCROLL ANIMATIONS
  // ============================================
  const ScrollAnimations = {
    observer: null,

    init() {
      const options = {
        root: null,
        rootMargin: '0px 0px -15% 0px',
        threshold: 0.1
      };

      this.observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            // Add stagger delay based on index
            const siblings = Array.from(entry.target.parentElement?.children || [])
              .filter(el => el.hasAttribute('data-animate'));
            const index = siblings.indexOf(entry.target);
            const delay = index * 150;

            setTimeout(() => {
              entry.target.classList.add('is-visible');
              entry.target.classList.add('animate-fade-in-up');
            }, delay);

            this.observer.unobserve(entry.target);
          }
        });
      }, options);

      document.querySelectorAll('[data-animate]').forEach(el => {
        this.observer.observe(el);
      });
    }
  };

  // ============================================
  // PARALLAX (Subtle)
  // ============================================
  const Parallax = {
    init() {
      const heroImg = document.querySelector('.hero__bg img');
      if (!heroImg) return;

      window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        const rate = scrolled * 0.3;
        heroImg.style.transform = `translateY(${rate}px) scale(1.1)`;
      }, { passive: true });
    }
  };

  // ============================================
  // AMBIENT SOUND (Optional)
  // ============================================
  const AmbientSound = {
    audio: null,
    isPlaying: false,

    init() {
      // Could add ambient nature sounds
      // Activated by user interaction
    },

    toggle() {
      if (!this.audio) return;
      if (this.isPlaying) {
        this.audio.pause();
      } else {
        this.audio.play();
      }
      this.isPlaying = !this.isPlaying;
    }
  };

  // ============================================
  // INITIALIZE
  // ============================================
  function init() {
    IntroOverlay.init();
    Navigation.init();
    ScrollAnimations.init();
    Parallax.init();

    console.log('%c Alexandria Sanctuary ', 'background: #c9a227; color: #0a1628; padding: 8px 16px; font-family: Georgia; font-size: 14px;');
    console.log('Where wisdom meets mortality.');
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

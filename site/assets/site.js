'use strict';

const viewer = document.querySelector('#viewer');
const entries = Array.from(document.querySelectorAll('.case-link'));
const viewImage = document.querySelector('#viewer-image');
const viewTitle = document.querySelector('#viewer-title');
const viewIndex = document.querySelector('#viewer-index');
let activeIndex = 0;
let returnFocus;

function showCase(index) {
  activeIndex = (index + entries.length) % entries.length;
  const entry = entries[activeIndex];
  viewImage.src = entry.href;
  viewImage.alt = 'Исходный скриншот публикации «' + entry.dataset.title + '» с названием и просмотрами';
  viewTitle.textContent = entry.dataset.title;
  viewIndex.textContent = String(activeIndex + 1).padStart(2, '0') + ' / ' + String(entries.length).padStart(2, '0');
}

if (typeof viewer.showModal === 'function') {
  document.querySelectorAll('[data-view], [data-hero]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.shiftKey || event.altKey || event.metaKey || event.button !== 0) return;
      const index = entries.findIndex(entry => entry.dataset.view === (link.dataset.view || link.dataset.hero));
      if (index < 0) return;
      event.preventDefault();
      returnFocus = link;
      showCase(index);
      viewer.showModal();
    });
  });
  viewer.querySelectorAll('[data-step]').forEach(button => {
    button.addEventListener('click', () => showCase(activeIndex + Number(button.dataset.step)));
  });
  viewer.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      showCase(activeIndex + (event.key === 'ArrowLeft' ? -1 : 1));
    }
  });
  viewer.addEventListener('click', event => {
    const rect = viewer.getBoundingClientRect();
    if (event.target === viewer && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) viewer.close();
  });
  viewer.addEventListener('close', () => returnFocus?.focus({preventScroll: true}));
}

const menu = document.querySelector('.menu');
menu.addEventListener('click', event => {
  if (event.target.closest('a')) menu.open = false;
});
document.addEventListener('click', event => {
  if (!menu.contains(event.target)) menu.open = false;
});
document.addEventListener('keydown', event => {
  if (menu.open && event.key === 'Escape') {
    menu.open = false;
    menu.querySelector('summary').focus();
  }
});

const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const scene = document.querySelector('.scene');
const production = document.querySelector('.production');
const studio = production.querySelector('.cut-studio');

// The cover stack keeps its original travel; each cut-out has its own depth.
function attachParallax(surface, target, scale, normalise) {
  function reset() {
    target.style.removeProperty('--x');
    target.style.removeProperty('--y');
  }
  surface.addEventListener('pointermove', event => {
    if (event.pointerType !== 'mouse' || reduced.matches) return;
    const rect = surface.getBoundingClientRect();
    let x = event.clientX - rect.left - rect.width / 2;
    let y = event.clientY - rect.top - rect.height / 2;
    if (normalise) {
      x /= rect.width / 2;
      y /= rect.height / 2;
    }
    target.style.setProperty('--x', x * scale + 'px');
    target.style.setProperty('--y', y * scale + 'px');
  });
  surface.addEventListener('pointerleave', reset);
  reduced.addEventListener('change', reset);
}
attachParallax(scene, scene, .012, false);
attachParallax(production, studio, 19, true);

if ('IntersectionObserver' in window && !reduced.matches) {
  const observer = new IntersectionObserver(events => {
    for (const event of events) {
      if (!event.isIntersecting) continue;
      const item = event.target;
      observer.unobserve(item);
      if (reduced.matches) continue;
      item.classList.add('arrived');
    }
  }, {threshold: .12});
  document.querySelectorAll('.case').forEach(item => observer.observe(item));
}

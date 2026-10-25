(function () {
  var choice = 'system';
  try { choice = localStorage.getItem('meep-theme') || 'system'; } catch (_) {}
  if (['system', 'light', 'dark'].indexOf(choice) < 0) choice = 'system';
  var dark = choice === 'dark' || (choice === 'system' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
  window.meepThemeChoice = choice;
})();
